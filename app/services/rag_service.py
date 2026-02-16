"""Servicio RAG con MongoDB Vector Search."""
from app.database.collections import get_knowledge_base_collection
from typing import List, Dict, Optional
import numpy as np


async def search_knowledge(
    query_embedding: List[float],
    scope: str,
    limit: int = 5
) -> List[Dict]:
    """
    Buscar en knowledge base usando vector search.
    
    Args:
        query_embedding: Embedding de la consulta
        scope: "global", "jonathan", o "pablo"
        limit: Número máximo de resultados
    
    Returns:
        Lista de documentos encontrados (sin source_id)
    """
    collection = get_knowledge_base_collection()
    
    # Determinar scopes a buscar
    if scope == "global":
        scopes_to_search = ["jonathan", "pablo"]
    else:
        scopes_to_search = [scope]
    
    results = []
    
    for search_scope in scopes_to_search:
        # Búsqueda vectorial usando $vectorSearch (MongoDB Atlas) o similitud coseno manual
        # Nota: Para MongoDB local, usamos similitud coseno manual
        cursor = collection.find({"scope": search_scope})
        
        async for doc in cursor:
            if "embedding" in doc and doc["embedding"]:
                # Calcular similitud coseno
                similarity = cosine_similarity(query_embedding, doc["embedding"])
                
                # Preparar resultado sin source_id
                result = {
                    "scope": doc.get("scope"),
                    "sections": doc.get("sections", {}),
                    "similarity": similarity
                }
                results.append(result)
    
    # Ordenar por similitud y limitar
    results.sort(key=lambda x: x["similarity"], reverse=True)
    results = results[:limit]
    
    # Eliminar campo similarity antes de retornar
    for result in results:
        result.pop("similarity", None)
    
    return results


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calcular similitud coseno entre dos vectores."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


async def get_embedding(text: str, api_key: str, base_url: str, model: str) -> List[float]:
    """
    Obtener embedding de texto usando OpenRouter.
    
    Nota: OpenRouter puede no tener endpoint de embeddings directo.
    Esta función puede necesitar usar un modelo específico o servicio alternativo.
    """
    import httpx
    
    # Para embeddings, podríamos usar un modelo específico o servicio alternativo
    # Por ahora, usamos un modelo que soporte embeddings
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://portfolio-backend",
                "X-Title": "Portfolio Backend"
            },
            json={
                "model": "text-embedding-3-small",  # Modelo de embeddings
                "input": text
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
