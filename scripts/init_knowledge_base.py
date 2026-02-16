"""Script para inicializar knowledge_base con embeddings."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.collections import get_knowledge_base_collection
from app.services.rag_service import get_embedding
from app.config import settings


# Datos de ejemplo para poblar la knowledge base
KNOWLEDGE_DATA = {
    "jonathan": {
        "sections": {
            "experience": "Jonathan tiene 5 años de experiencia en desarrollo full-stack, especializado en Python, FastAPI, React y sistemas cloud.",
            "skills": "Python, FastAPI, React, TypeScript, MongoDB, PostgreSQL, AWS, Docker, Kubernetes",
            "projects": "Desarrollo de APIs RESTful escalables, aplicaciones web modernas con React, sistemas de microservicios",
            "services": "Desarrollo backend, arquitectura de software, consultoría técnica, mentoring"
        }
    },
    "pablo": {
        "sections": {
            "experience": "Pablo tiene 4 años de experiencia en desarrollo frontend y diseño UX/UI, especializado en React, Astro y diseño de interfaces modernas.",
            "skills": "React, Astro, TypeScript, Tailwind CSS, Figma, Next.js, Node.js",
            "projects": "Aplicaciones web responsivas, sistemas de diseño, optimización de performance frontend, PWA",
            "services": "Desarrollo frontend, diseño UI/UX, optimización web, consultoría frontend"
        }
    }
}


async def init_knowledge_base():
    """Inicializar knowledge_base con datos y embeddings."""
    print("🚀 Inicializando knowledge_base...")
    
    # Conectar a MongoDB
    await connect_to_mongo()
    
    collection = get_knowledge_base_collection()
    
    # Limpiar colección existente (opcional, comentar si quieres mantener datos)
    # await collection.delete_many({})
    
    for scope, data in KNOWLEDGE_DATA.items():
        print(f"📝 Procesando scope: {scope}")
        
        # Combinar todas las secciones en un texto para el embedding
        full_text = "\n".join([
            f"{section_name}: {section_content}"
            for section_name, section_content in data["sections"].items()
        ])
        
        try:
            # Obtener embedding
            print(f"  🔄 Generando embedding para {scope}...")
            embedding = await get_embedding(
                full_text,
                settings.openrouter_api_key,
                settings.openrouter_base_url,
                "text-embedding-3-small"
            )
            
            # Insertar documento
            document = {
                "scope": scope,
                "sections": data["sections"],
                "embedding": embedding
            }
            
            # Upsert (actualizar si existe, insertar si no)
            await collection.update_one(
                {"scope": scope},
                {"$set": document},
                upsert=True
            )
            
            print(f"  ✅ {scope} procesado exitosamente")
            
        except Exception as e:
            print(f"  ❌ Error procesando {scope}: {e}")
            continue
    
    # Crear índice para búsquedas eficientes (si MongoDB lo soporta)
    try:
        await collection.create_index("scope")
        print("✅ Índice creado en 'scope'")
    except Exception as e:
        print(f"⚠️  No se pudo crear índice: {e}")
    
    print("\n✨ Knowledge base inicializada exitosamente!")
    
    # Cerrar conexión
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(init_knowledge_base())
