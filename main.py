import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.connection import init_db, close_db
from app.middleware.request_id import RequestIdMiddleware
from app.routes import chat, conversation, health
from app.scheduler.daily_cleanup import start_scheduler, stop_scheduler
from app.services.knowledge_service import load_knowledge_cache
from app.services.langsmith_tracer import ensure_langsmith_env
from app.services.prompt_service import load_prompts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_required()
    init_db()
    load_prompts()
    load_knowledge_cache()
    ensure_langsmith_env()
    start_scheduler()
    logger.info("Application started successfully")
    yield
    stop_scheduler()
    close_db()
    logger.info("Application shut down")


app = FastAPI(title="Portfolio Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(conversation.router)


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data."},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.exception("Internal server error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )
