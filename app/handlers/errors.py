from __future__ import annotations
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import RetryAfter, TimedOut, NetworkError

log = logging.getLogger(__name__)

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, (RetryAfter, TimedOut, NetworkError)):
        log.warning("Transient telegram error: %s", err)
        return
    log.exception("Handler error", exc_info=err)
