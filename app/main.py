from __future__ import annotations
import asyncio, logging, signal, os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, AIORateLimiter
from telegram.error import InvalidToken
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration

from .config import Settings
from .logging_config import setup_logging
from .repository.db import Database
from .handlers import basic, admin, errors
from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat

async def _register_commands(application, admin_ids: list[int]) -> None:
    default_cmds = [
        BotCommand("start", "Проверка, что бот жив"),
        BotCommand("help", "Список команд"),
        BotCommand("id", "Показать ваш chat_id"),
    ]
    admin_extra = [
        BotCommand("stats", "Статистика (админ)"),
        BotCommand("broadcast", "Рассылка (админ)"),
    ]
    await application.bot.set_my_commands(default_cmds, scope=BotCommandScopeAllPrivateChats())
    for uid in admin_ids:
        try:
            await application.bot.set_my_commands(default_cmds + admin_extra, scope=BotCommandScopeChat(chat_id=uid))
        except Exception:
            pass

async def run():
    settings = Settings.from_env()
    setup_logging(settings.ENV)

    if settings.SENTRY_DSN:
        sentry_init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=0.02,
            environment=settings.ENV,
            integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
        )

    try:
        application = (
            Application.builder()
            .token(settings.BOT_TOKEN)
            .concurrent_updates(True)
            .rate_limiter(AIORateLimiter())
            .build()
        )
    except InvalidToken as e:
        logging.getLogger(__name__).error("Invalid BOT_TOKEN: %s", e)
        raise

    db = Database(settings.DATABASE_URL)
    await db.connect()

    application.add_handler(CommandHandler("start", basic.start))
    application.add_handler(CommandHandler("help", basic.help_cmd))
    application.add_handler(CommandHandler("id", basic.show_id))
    application.add_handler(CommandHandler("stats", admin.stats))
    application.add_handler(CommandHandler("broadcast", admin.broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, basic.echo))
    application.add_error_handler(errors.on_error)

    application.bot_data["db"] = db
    application.bot_data["admins"] = settings.ADMIN_IDS

    await application.initialize()
    await _register_commands(application, settings.ADMIN_IDS)

    # Ставим вебхук
    base = settings.BASE_URL.strip().rstrip("/")
    url_path = f"/bot/{settings.WEBHOOK_SECRET}"
    webhook_url = f"{base}{url_path}"

    await application.bot.set_webhook(url=webhook_url, secret_token=settings.WEBHOOK_SECRET)
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        url_path=url_path,
        secret_token=settings.WEBHOOK_SECRET,
    )

    stop_event = asyncio.Event()
    def _signal_handler(*_): stop_event.set()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _signal_handl
