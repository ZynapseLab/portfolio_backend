"""Sistema de logging JSON."""
import json
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import settings
import hashlib


def hash_ip(ip: str) -> str:
    """Hashear IP para privacidad."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


async def log_request(
    request_id: str,
    ip_hash: str,
    scope: str,
    status: str,
    latency: float,
    classification: Optional[str] = None
):
    """Registrar request en archivo JSON."""
    log_entry = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_hash": ip_hash,
        "scope": scope,
        "status": status,
        "latency": latency,
        "classification": classification
    }
    
    # Crear directorio de logs si no existe
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Archivo de log diario
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = log_dir / f"requests_{today}.jsonl"
    
    # Escribir en formato JSONL (una línea por entrada)
    async with aiofiles.open(log_file, "a") as f:
        await f.write(json.dumps(log_entry) + "\n")
