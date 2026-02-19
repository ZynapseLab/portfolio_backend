"""
Configuración de observabilidad con LangSmith para el grafo del agente.

LangSmith captura automáticamente las trazas del grafo (nodos, entradas/salidas,
latencia) cuando LANGSMITH_TRACING está activo. Este módulo centraliza:
- Poner las variables de entorno que el SDK de LangChain/LangGraph espera.
- Construir el config (tags, metadata) por request para filtrar en LangSmith.
- Context manager por request para delimitar la traza.
"""

import os

from langchain_core.tracers import LangChainTracer
from langsmith import Client
from langsmith.anonymizer import create_anonymizer

from app.config import settings


anonymizer = create_anonymizer(
    [
        # Matches Public IPv4 addresses
        {"pattern": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", "replacement": "0.0.0.0"},
        # Matches Public IPv6 addresses
        {"pattern": r"^[0-9a-fA-F:]+$", "replacement": "::"},
        # Matches email addresses
        {
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "replacement": "email@example.com",
        },
        # Matches phone numbers
        {"pattern": r"^\d{10}$", "replacement": "1234567890"},
    ]
)

# Create the tracer client and tracer
tracer_client = Client(api_key=settings.LANGSMITH_API_KEY, anonymizer=anonymizer)
tracer = LangChainTracer(client=tracer_client)


def ensure_langsmith_env() -> None:
    """
    Configura las variables de entorno que LangSmith/LangChain usan para tracing.
    Llamar una vez al arranque si quieres que el tracing use los valores de Settings.
    """
    if not settings.LANGSMITH_TRACING or not settings.LANGSMITH_API_KEY:
        return
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT


def get_trace_config(
    request_id: str,
    ip: str,
    scope: str,
) -> dict:
    """
    Config para ainvoke/invoke del grafo: tags y metadata por request.
    Permite filtrar y agrupar trazas en LangSmith por scope, request_id, etc.
    """
    return {
        "run_name": f"chat/{request_id}",
        "tags": ["chat", f"scope:{scope}"],
        "metadata": {
            "request_id": request_id,
            "ip": ip,
            "scope": scope,
        },
    }
