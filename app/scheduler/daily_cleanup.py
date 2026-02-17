import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.conversation_service import daily_cleanup
from app.utils.datetime_utils import utc_today

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _cleanup_job() -> None:
    today = utc_today()
    count = await daily_cleanup(today)
    logger.info("Daily cleanup: soft-deleted %d conversations before %s", count, today)


def start_scheduler() -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _cleanup_job,
        trigger=CronTrigger(hour=0, minute=5, timezone="UTC"),
        id="daily_cleanup",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started: daily cleanup at 00:05 UTC")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
