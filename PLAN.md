Aquí tienes las **historias de usuario convertidas a Markdown técnico**, con lenguaje mejorado, consistente y optimizado para desarrolladores. He mantenido todas tus decisiones, pero con **claridad de implementación, criterios de aceptación y contratos explícitos**.

---

# 🧩 EPIC 1 — Frontend Portfolio IA (Astro + React Islands)

---

# 🟦 US-01 — Chatbot Global en `/`

## 👤 Actor

Visitante del portfolio

## 🎯 Objetivo

Permitir al visitante interactuar con un chatbot en la página principal (`/`) para conocer las habilidades, servicios y experiencia del equipo.

---

## 📐 Requisitos funcionales

### Scope

```text
scope = global
```

---

### Rate limit

* Límite: **10 mensajes por día por IP**
* Zona horaria: **UTC**
* Controlado por backend

---

### Gestión de sesión

El backend debe emitir una **cookie httpOnly** con un JWT que contenga:

```json
{
  "ip": "string",
  "scope": "string",
  "messages_used": "number",
  "date": "YYYY-MM-DD"
}
```

Restricciones:

* No accesible desde JavaScript
* No reiniciable manualmente por el usuario

---

### Comunicación

Streaming mediante:

```http
Content-Type: application/x-ndjson
```

Headers obligatorios:

```http
X-Messages-Used
X-Messages-Limit
X-Reset-At
```

---

## 🎨 Requisitos de UI

La interfaz debe incluir:

* Estilo visual tipo **startup tecnológica**
* Streaming de respuesta **token por token**
* Lista de **sugerencias predefinidas**
* Contador diario visible
* Barra de progreso de uso
* Toast notifications elegantes
* Botón **"Borrar conversación"**
* Input deshabilitado al alcanzar el límite diario

---

## 🧠 Persistencia de conversación

La conversación debe estar asociada a:

```text
ip
scope
date
```

Solo deben mostrarse mensajes del scope actual.

---

## ✅ Criterios de aceptación

* El usuario puede enviar mensajes hasta alcanzar el límite diario
* El chatbot responde mediante streaming NDJSON
* El contador y progreso se actualizan correctamente
* El input se bloquea al alcanzar el límite

---

# 🟦 US-02 — Rutas dinámicas de desarrollador `/[developer]`

## 👤 Actor

Cliente o reclutador

## 🎯 Objetivo

Permitir visualizar el perfil individual de cada desarrollador.

---

## 📐 Rutas

Ejemplo:

```text
/jonathan
/pablo
```

---

## 📊 Contenido

Renderizado estático con Astro:

* Skills
* Experiencia
* Stack tecnológico
* Proyectos

---

## 🤖 Chatbot asociado

El chatbot debe usar un scope dinámico:

```text
scope = jonathan
scope = pablo
```

---

## 🧠 Comportamiento

* Historial aislado por scope
* Cambio de scope inicia nueva sesión backend
* Arquitectura preparada para agregar nuevos developers

---

## ✅ Criterios de aceptación

* Cada developer tiene su propio historial independiente
* El chatbot responde dentro del contexto correcto

---

# 🟦 US-03 — Sistema conversacional UI

## 👤 Actor

Usuario

## 🎯 Objetivo

Proveer una experiencia conversacional moderna y fluida.

---

## 🎨 Requisitos UI

La interfaz debe incluir:

* Streaming animado
* Auto-scroll automático
* Indicador de typing
* Contador diario visible
* Botón borrar conversación
* Toast de confirmación al borrar

---

## 🧠 Borrado de conversación

Acción:

```text
Soft delete
```

Efectos:

* Elimina el contexto conversacional
* NO reinicia el contador diario

---

## ✅ Criterios de aceptación

* La conversación desaparece del frontend
* El límite diario se mantiene intacto

---

# 🟦 US-04 — Sistema de sesión frontend

## 👤 Actor

Sistema

## 🎯 Objetivo

Gestionar la sesión del usuario automáticamente.

---

## 📐 Requisitos

* Cookie httpOnly
* No accesible por JS
* Expiración automática diaria

---

## 🌗 Tema visual

Debe soportar:

* Dark mode
* Light mode

Comportamiento:

* Detecta preferencia del sistema
* Persistido en:

```text
localStorage
```

---

## ✅ Criterios de aceptación

* La sesión funciona sin intervención manual
* El tema se mantiene entre sesiones

---

---

# 🟥 EPIC 2 — Backend Inteligente

Stack:

* FastAPI
* LangGraph
* MongoDB
* Mongo Vector Search
* OpenRouter
* JWT manual
* NDJSON Streaming

---

# 🟦 US-05 — Endpoint `/chat`

## 👤 Actor

Frontend

## 🎯 Objetivo

Enviar mensajes y recibir respuestas del chatbot.

---

## 📥 Request

```http
POST /chat
```

Body:

```json
{
  "message": "string",
  "scope": "global | jonathan | pablo"
}
```

---

## 📤 Response

Streaming NDJSON:

```json
{"type":"token","data":"Hola"}
{"type":"token","data":" Pablo"}
{"type":"done"}
```

---

## 📬 Headers obligatorios

```http
X-Messages-Used
X-Messages-Limit
X-Reset-At
```

---

## 🔐 Seguridad

JWT manual en cookie httpOnly.

Payload:

```json
{
  "ip": "string",
  "scope": "string",
  "messages_used": "number",
  "date": "string"
}
```

---

## 📊 Logging

Archivo local en formato JSON:

```json
{
  "request_id": "string",
  "ip_hash": "string",
  "scope": "string",
  "status": "string",
  "latency": "number"
}
```

---

## ✅ Criterios de aceptación

* Streaming funcional
* Headers correctos
* Rate limit aplicado

---

# 🟦 US-06 — Agente LangGraph restringido

## 👤 Actor

Sistema

## 🎯 Objetivo

Restringir el chatbot al dominio del portfolio.

---

## 🧠 Flujo

```text
Input
↓
Clasificador
↓
Resultado:
IN_DOMAIN
OUT_OF_DOMAIN
PROMPT_INJECTION
CONTACT
```

---

## 🚫 OUT_OF_DOMAIN

Debe responder:

* Mensaje predefinido
* Traducido al idioma original
* Sin explicar el motivo

---

## 🛡 PROMPT_INJECTION

Debe responder:

* Mensaje seguro predefinido
* Sin explicar el motivo

---

## 🤝 Identidad

Siempre responde como:

```text
Equipo conjunto
```

Nunca como individuos separados.

---

## ✅ Criterios de aceptación

* Clasificación correcta
* No filtra prompts internos

---

# 🟦 US-07 — Sistema RAG

## 👤 Actor

Agente

## 🎯 Objetivo

Acceder a conocimiento vectorial.

---

## 🗄 Colección Mongo

```text
knowledge_base
```

Documento:

```json
{
  "scope": "string",
  "sections": {
    "experience": "...",
    "skills": "...",
    "projects": "...",
    "services": "..."
  },
  "embedding": []
}
```

---

## 🔎 Búsqueda

Reglas:

Scope global:

```text
jonathan + pablo
```

Scope individual:

```text
solo ese developer
```

---

## 🔐 Restricciones

NO debe devolver:

```text
source_id
```

---

## ✅ Criterios de aceptación

* El agente usa contexto vectorial correctamente

---

# 🟦 US-08 — Tool envío de correos

## 👤 Actor

Cliente

## 🎯 Objetivo

Contactar al equipo.

---

## 📥 Input

Campos:

* name
* email
* country
* subject
* message

Restricción:

```text
message <= 500 caracteres
```

---

## 📤 Acción

Enviar correo a:

* Jonathan
* Pablo
* Usuario (copia)

---

## 🗄 Persistencia

Colección:

```text
contact_leads
```

---

## 🔒 Rate limit

Por IP:

```text
2 correos por día
```

---

## 🔁 Retries internos

```text
5 intentos
```

---

## ✅ Criterios de aceptación

* El correo se envía correctamente
* El límite se respeta

---

# 🟦 US-09 — Sistema seguro de prompts

## 👤 Actor

Sistema

## 🎯 Objetivo

Gestionar prompts sin exponerlos.

---

## 🗄 Colección

```text
prompts
```

---

## 🔐 Restricciones

No permitido:

* Versionado
* Exposición
* Almacenamiento de ataques

---

## ✅ Criterios de aceptación

* Prompts no accesibles externamente

---

# 🟦 US-10 — Persistencia de conversaciones

## 👤 Actor

Usuario

## 🎯 Objetivo

Persistir conversaciones.

---

## 🗄 Colección

```text
conversations
```

Documento:

```json
{
  "ip": "string",
  "scope": "string",
  "date": "string",
  "messages": [],
  "messages_used": 0,
  "deleted": false
}
```

---

## 🧹 Eliminación

Soft delete mediante:

```http
DELETE /conversation
```

Requiere:

JWT válido

---

## 🕒 Limpieza automática

Soft delete diario mediante procedimiento almacenado.

---

## ✅ Criterios de aceptación

* Conversaciones eliminables
* No eliminación física

---

# 🟦 US-11 — Rate limit

## 🎯 Objetivo

Controlar uso diario.

---

## 📊 Límites

Chat:

```text
10 mensajes / día
```

Email:

```text
2 por día
```

---

## 🌍 Zona horaria

```text
UTC
```

---

## 📤 Error

```http
429
```

Body:

```json
{
"type":"rate_limit",
"limit":10,
"used":10,
"reset_at":"ISO8601"
}
```

---

# 🟦 US-12 — Sistema de logs

## 👤 Actor

Equipo de desarrollo

## 🎯 Objetivo

Permitir trazabilidad.

---

## 📄 Almacenamiento

Archivo local

Formato JSON

---

## 📊 Campos

```json
{
  "request_id": "string",
  "timestamp": "string",
  "ip_hash": "string",
  "scope": "string",
  "status": "string",
  "latency": "number",
  "classification": "string"
}
```
