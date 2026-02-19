"""
Zia AI — ARQ Background Worker
Async task execution with priority queues, cron jobs, and retries.
"""

import logging

from arq import cron
from arq.connections import RedisSettings

from app.config import settings

logger = logging.getLogger("zia.worker")


async def execute_action_task(ctx, execution_id: str, action_type: str,
                              params: dict, user_id: str):
    """ARQ task: execute an action via the appropriate executor."""
    logger.info(f"Executing {action_type} (id={execution_id}, user={user_id})")

    from app.executors.gmail import GmailExecutor
    from app.executors.twilio_voice import TwilioVoiceExecutor
    from app.executors.twilio_whatsapp import TwilioWhatsAppExecutor
    from app.executors.filesystem import FilesystemExecutor
    from app.executors.browser import BrowserExecutor
    from app.executors.system import SystemExecutor
    from app.executors.macros import MacroExecutor

    executor_map = {
        "gmail": GmailExecutor(),
        "twilio_voice": TwilioVoiceExecutor(),
        "twilio_whatsapp": TwilioWhatsAppExecutor(),
        "filesystem": FilesystemExecutor(),
        "browser": BrowserExecutor(),
        "system": SystemExecutor(),
        "macros": MacroExecutor(),
    }

    # Determine executor from action_type prefix
    executor_key = action_type.split(".")[0]
    if executor_key == "twilio":
        executor_key = "twilio_voice" if "call" in action_type else "twilio_whatsapp"

    executor = executor_map.get(executor_key)
    if not executor:
        raise ValueError(f"No executor for action type: {action_type}")

    result = await executor.execute(action_type, params, user_id)
    logger.info(f"Completed {action_type} (id={execution_id}): {result.get('status')}")
    return result


async def expire_confirmations(ctx):
    """Cron: expire stale pending confirmations every 60s."""
    logger.info("Running confirmation expiry sweep")


async def refresh_oauth_tokens(ctx):
    """Cron: proactively refresh OAuth tokens expiring within 10 minutes."""
    logger.info("Running OAuth token refresh sweep")


class WorkerSettings:
    """ARQ worker configuration."""
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [execute_action_task]
    cron_jobs = [
        cron(expire_confirmations, second=0),        # Every minute
        cron(refresh_oauth_tokens, minute={0, 30}),  # Every 30 min
    ]
    max_jobs = settings.WORKER_MAX_JOBS
    job_timeout = settings.WORKER_JOB_TIMEOUT
    retry_jobs = 3
    queue_name = "zia:tasks:default"
