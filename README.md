# Portfolio Backend

Backend del portfolio construido con FastAPI, LangGraph, MongoDB Vector Search y OpenRouter.

## 🚀 Características

- **Chatbot inteligente** con streaming NDJSON
- **Sistema RAG** usando MongoDB Vector Search
- **Rate limiting** por IP y scope (10 mensajes/día chat, 2 emails/día)
- **Autenticación JWT** con cookies httpOnly
- **Clasificación de intenciones** (IN_DOMAIN, OUT_OF_DOMAIN, PROMPT_INJECTION, CONTACT)
- **Persistencia de conversaciones** con soft delete
- **Sistema de logs** en formato JSON
- **Envío de correos** con retries automáticos

## 📋 Requisitos

- Python 3.10+
- MongoDB 6.0+ (con soporte para Vector Search recomendado)
- Cuenta de OpenRouter con API key
- Servidor SMTP para envío de correos

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone <repo-url>
cd portfolio_backend
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
- `MONGODB_URI`: URI de conexión a MongoDB
- `OPENROUTER_API_KEY`: API key de OpenRouter
- `JWT_SECRET_KEY`: Clave secreta para JWT (generar una aleatoria)
- Configuración SMTP para envío de correos
- Emails de contacto

5. **Inicializar knowledge base:**
```bash
python scripts/init_knowledge_base.py
```

Este script poblará la colección `knowledge_base` con datos de ejemplo y generará los embeddings necesarios.

## 🏃 Ejecución

### Desarrollo
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en `http://localhost:8000`

## 📚 Endpoints

### POST `/api/chat`
Endpoint principal de chat con streaming NDJSON.

**Request:**
```json
{
  "message": "¿Cuáles son tus habilidades?",
  "scope": "global"
}
```

**Response:** Streaming NDJSON
```
{"type":"token","data":"Hola"}
{"type":"token","data":" Pablo"}
{"type":"done"}
```

**Headers de respuesta:**
- `X-Messages-Used`: Mensajes usados hoy
- `X-Messages-Limit`: Límite diario
- `X-Reset-At`: Fecha/hora de reset (ISO8601)

### DELETE `/api/conversation`
Soft delete de la conversación actual. NO reinicia el contador de mensajes.

### GET `/health`
Health check endpoint.

### GET `/docs`
Documentación interactiva de la API (Swagger UI).

## 🗄️ Estructura de Base de Datos

### Colecciones MongoDB

#### `knowledge_base`
Documentos con información de developers y embeddings:
```json
{
  "scope": "jonathan",
  "sections": {
    "experience": "...",
    "skills": "...",
    "projects": "...",
    "services": "..."
  },
  "embedding": [0.123, 0.456, ...]
}
```

#### `conversations`
Historial de conversaciones:
```json
{
  "ip": "192.168.1.1",
  "scope": "global",
  "date": "2026-02-16",
  "messages": [...],
  "messages_used": 5,
  "deleted": false
}
```

#### `contact_leads`
Formularios de contacto:
```json
{
  "name": "...",
  "email": "...",
  "country": "...",
  "subject": "...",
  "message": "...",
  "created_at": "2026-02-16T10:00:00Z"
}
```

#### `prompts`
Prompts del sistema (no expuestos externamente):
```json
{
  "name": "system",
  "content": "..."
}
```

## 🔧 Scripts

### Inicializar Knowledge Base
```bash
python scripts/init_knowledge_base.py
```

### Limpieza de Conversaciones
```bash
python scripts/cleanup_conversations.py [días_a_mantener]
```

Por defecto mantiene 30 días. Ejecutar diariamente como cron job.

## 🔒 Seguridad

- Cookies httpOnly para JWT
- Rate limiting por IP
- Validación de inputs
- Hash de IPs en logs
- Soft delete para auditoría
- Prompts no expuestos externamente

## 📝 Logs

Los logs se guardan en formato JSONL en el directorio `logs/`:
- Un archivo por día: `requests_YYYY-MM-DD.jsonl`
- Campos: `request_id`, `timestamp`, `ip_hash`, `scope`, `status`, `latency`, `classification`

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest
```

## 📦 Despliegue

1. Configurar variables de entorno en producción
2. Usar un servidor ASGI como Gunicorn con Uvicorn workers
3. Configurar MongoDB Atlas para Vector Search en producción
4. Configurar cron job para limpieza diaria de conversaciones
5. Configurar reverse proxy (nginx) con SSL

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y propietario.

## 🆘 Soporte

Para problemas o preguntas, contactar al equipo de desarrollo.
