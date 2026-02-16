"""Aplicación FastAPI principal."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routes import chat, conversation, health, contact


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversation.router, prefix="/api", tags=["conversation"])
app.include_router(contact.router, prefix="/api", tags=["contact"])
app.include_router(health.router, tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación."""
    await close_mongo_connection()


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "Portfolio Backend API",
        "version": settings.app_version,
        "docs": "/docs"
    }
