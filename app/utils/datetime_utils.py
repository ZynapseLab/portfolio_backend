from datetime import datetime, timezone, timedelta


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_today() -> str:
    return utc_now().strftime("%Y-%m-%d")


def utc_now_iso() -> str:
    return utc_now().isoformat()


def get_reset_at() -> str:
    now = utc_now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow.isoformat()
