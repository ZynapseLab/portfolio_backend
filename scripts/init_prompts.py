"""Script para inicializar prompts del sistema."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.services.prompt_service import set_prompt


SYSTEM_PROMPT = """Eres un asistente del equipo de desarrollo del portfolio. 
Tu objetivo es ayudar a los visitantes a conocer las habilidades, experiencia y proyectos del equipo.

IMPORTANTE:
- Responde SIEMPRE como "equipo conjunto", nunca como individuos separados
- Usa el contexto proporcionado para responder preguntas sobre habilidades, experiencia y proyectos
- Sé profesional pero amigable
- Si no tienes información suficiente en el contexto, indica que puedes ayudar con información general del equipo
- Mantén las respuestas concisas pero informativas
- Si alguien pregunta sobre contacto, indica que pueden usar el formulario de contacto"""


async def init_prompts():
    """Inicializar prompts del sistema."""
    print("🚀 Inicializando prompts del sistema...")
    
    # Conectar a MongoDB
    await connect_to_mongo()
    
    # Establecer prompt del sistema
    await set_prompt("system", SYSTEM_PROMPT)
    print("✅ Prompt 'system' inicializado")
    
    # Cerrar conexión
    await close_mongo_connection()
    
    print("✨ Prompts inicializados exitosamente!")


if __name__ == "__main__":
    asyncio.run(init_prompts())
