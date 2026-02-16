"""Agente LangGraph para el chatbot."""
from typing import AsyncGenerator, Dict, List, TypedDict
from app.agents.classifier import classify_message, get_out_of_domain_response, get_prompt_injection_response, detect_language
from app.services.rag_service import search_knowledge, get_embedding
from app.services.prompt_service import get_prompt
from app.config import settings
import httpx
import json


class AgentState(TypedDict):
    """Estado del agente durante el procesamiento."""
    message: str
    scope: str
    classification: str
    rag_context: List[Dict]
    response: str
    language: str


def classify_node(state: AgentState) -> AgentState:
    """Nodo de clasificación."""
    state["classification"] = classify_message(state["message"])
    state["language"] = detect_language(state["message"])
    return state


async def rag_node(state: AgentState) -> AgentState:
    """Nodo de RAG - buscar contexto."""
    if state["classification"] != "IN_DOMAIN":
        return state
    
    try:
        # Obtener embedding de la consulta
        query_embedding = await get_embedding(
            state["message"],
            settings.openrouter_api_key,
            settings.openrouter_base_url,
            "text-embedding-3-small"
        )
        
        # Buscar en knowledge base
        state["rag_context"] = await search_knowledge(
            query_embedding,
            state["scope"],
            limit=3
        )
    except Exception as e:
        print(f"Error en RAG: {e}")
        state["rag_context"] = []
    
    return state


async def generate_response_node(state: AgentState) -> AsyncGenerator[str, None]:
    """Nodo de generación de respuesta."""
    if state["classification"] == "OUT_OF_DOMAIN":
        response = get_out_of_domain_response(state["language"])
        for char in response:
            yield char
        return
    
    if state["classification"] == "PROMPT_INJECTION":
        response = get_prompt_injection_response(state["language"])
        for char in response:
            yield char
        return
    
    if state["classification"] == "CONTACT":
        # Para contacto, el agente debe indicar que use el tool
        response = "Para contactarnos, por favor proporciona tu nombre, email, país, asunto y mensaje. Te ayudaré a enviar tu mensaje."
        for char in response:
            yield char
        return
    
    # IN_DOMAIN: Generar respuesta usando LLM con contexto RAG
    try:
        # Construir prompt del sistema
        system_prompt = await get_prompt("system") or "Eres un asistente del equipo de desarrollo. Responde siempre como equipo conjunto, nunca como individuos separados. Usa el contexto proporcionado para responder preguntas sobre habilidades, experiencia y proyectos."
        
        # Construir contexto de RAG
        context_text = ""
        if state["rag_context"]:
            for doc in state["rag_context"]:
                scope = doc.get("scope", "")
                sections = doc.get("sections", {})
                context_text += f"\n\nInformación de {scope}:\n"
                for section_name, section_content in sections.items():
                    context_text += f"{section_name}: {section_content}\n"
        
        # Construir mensaje completo
        user_message = f"Contexto:\n{context_text}\n\nPregunta del usuario: {state['message']}\n\nResponde de manera natural y útil usando el contexto proporcionado."
        
        # Generar respuesta con streaming usando OpenRouter directamente
        async for token in stream_openrouter_response(system_prompt, user_message):
            yield token
            
    except Exception as e:
        print(f"Error generando respuesta: {e}")
        error_msg = "Lo siento, hubo un error al generar la respuesta. Por favor intenta de nuevo."
        for char in error_msg:
            yield char


async def stream_openrouter_response(system_prompt: str, user_message: str) -> AsyncGenerator[str, None]:
    """Streaming de respuesta desde OpenRouter."""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://portfolio-backend",
                "X-Title": "Portfolio Backend",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "stream": True,
                "temperature": 0.7
            },
            timeout=60.0
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]  # Remover "data: "
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue


async def process_chat_message(
    message: str,
    scope: str
) -> AsyncGenerator[str, None]:
    """
    Procesar mensaje de chat usando el agente LangGraph.
    
    Args:
        message: Mensaje del usuario
        scope: Scope de la conversación
    
    Yields:
        Tokens de la respuesta
    """
    # Crear estado inicial
    state: AgentState = {
        "message": message,
        "scope": scope,
        "classification": "",
        "rag_context": [],
        "response": "",
        "language": "en"
    }
    
    # Ejecutar flujo del agente
    state = classify_node(state)
    
    if state["classification"] == "IN_DOMAIN":
        state = await rag_node(state)
    
    # Generar respuesta con streaming
    async for token in generate_response_node(state):
        yield token
