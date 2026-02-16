"""Clasificador de intenciones."""
from typing import Literal
import re


ClassificationType = Literal["IN_DOMAIN", "OUT_OF_DOMAIN", "PROMPT_INJECTION", "CONTACT"]


# Patrones para detección de prompt injection
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+instructions?",
    r"forget\s+(previous|all|above)",
    r"system\s*:",
    r"assistant\s*:",
    r"you\s+are\s+(now|a|an)",
    r"act\s+as\s+(if|though)",
    r"pretend\s+to\s+be",
    r"roleplay",
    r"jailbreak",
    r"bypass",
    r"override",
    r"\[INST\]",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
]


# Patrones para detección de contacto
CONTACT_PATTERNS = [
    r"contact",
    r"get\s+in\s+touch",
    r"reach\s+out",
    r"send\s+(an?\s+)?email",
    r"email\s+(me|you|us)",
    r"hire",
    r"work\s+together",
    r"collaborat",
    r"project\s+proposal",
]


def classify_message(message: str) -> ClassificationType:
    """
    Clasificar mensaje del usuario.
    
    Returns:
        IN_DOMAIN: Pregunta válida sobre el portfolio
        OUT_OF_DOMAIN: Fuera del dominio del portfolio
        PROMPT_INJECTION: Intento de inyección de prompt
        CONTACT: Solicitud de contacto
    """
    message_lower = message.lower().strip()
    
    # 1. Verificar prompt injection primero (más crítico)
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "PROMPT_INJECTION"
    
    # 2. Verificar si es solicitud de contacto
    for pattern in CONTACT_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return "CONTACT"
    
    # 3. Verificar si está fuera del dominio
    # Por ahora, asumimos que si no es prompt injection ni contacto, está en dominio
    # Esto se puede refinar con un modelo de clasificación más sofisticado
    
    # Palabras clave que indican fuera de dominio
    out_of_domain_keywords = [
        "weather", "time", "date", "joke", "story", "poem",
        "recipe", "sports", "news", "politics", "religion"
    ]
    
    # Si el mensaje contiene principalmente palabras fuera de dominio, clasificar como tal
    words = message_lower.split()
    out_of_domain_count = sum(1 for word in words if word in out_of_domain_keywords)
    
    if len(words) > 0 and out_of_domain_count / len(words) > 0.3:
        return "OUT_OF_DOMAIN"
    
    # Por defecto, asumir que está en dominio
    return "IN_DOMAIN"


def get_out_of_domain_response(language: str = "es") -> str:
    """Obtener respuesta predefinida para mensajes fuera de dominio."""
    responses = {
        "es": "Lo siento, solo puedo responder preguntas sobre nuestro portfolio, habilidades y experiencia. ¿Hay algo específico sobre nuestro trabajo que te gustaría conocer?",
        "en": "Sorry, I can only answer questions about our portfolio, skills, and experience. Is there something specific about our work you'd like to know?",
    }
    return responses.get(language, responses["en"])


def get_prompt_injection_response(language: str = "es") -> str:
    """Obtener respuesta segura predefinida para prompt injection."""
    responses = {
        "es": "No puedo ayudarte con esa solicitud. ¿Hay algo sobre nuestro portfolio que te gustaría conocer?",
        "en": "I can't help with that request. Is there something about our portfolio you'd like to know?",
    }
    return responses.get(language, responses["en"])


def detect_language(text: str) -> str:
    """Detectar idioma del texto (simple)."""
    # Detección simple basada en palabras comunes
    spanish_words = ["qué", "cómo", "cuándo", "dónde", "por qué", "también", "muy", "más"]
    english_words = ["what", "how", "when", "where", "why", "also", "very", "more"]
    
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    return "es" if spanish_count > english_count else "en"
