import os

import orjson

from app.config import settings
from app.utils.datetime_utils import utc_now_iso
from app.utils.hashing import hash_ip


def write_log(
    request_id: str,
    ip: str,
    scope: str,
    status: str,
    latency_ms: float,
    classification: str | None = None,
) -> None:
    log_entry = {
        "request_id": request_id,
        "ip_hash": hash_ip(ip),
        "scope": scope,
        "status": status,
        "latency_ms": round(latency_ms, 2),
        "classification": classification,
        "timestamp": utc_now_iso(),
    }

    log_path = settings.LOG_FILE_PATH
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "ab") as f:
        f.write(orjson.dumps(log_entry) + b"\n")
