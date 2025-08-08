from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes
import logging

log = logging.getLogger(__name__)

def _is_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    admins = set(context.application.bot_data.get("admins", []))
    return user_id in admins

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat:
        context.application.bot_data.setdefault("db_ready", True)
        await context.application.bot_data["db"].bump_user(chat.id)
    await update.effective_message.reply_text("✅ Бот запущен и готов. /help — список команд.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = bool(user and _is_admin(context, user.id))
    lines = [
        "Доступные команды:",
        "/start — проверить, что бот жив",
        "/help — помощь",
        "/id — показать ваш chat_id",
    ]
    if is_admin:
        lines += [
            "/stats — (админ) статистика",
            "/broadcast <текст> — (админ) рассылка",
        ]
    await update.effective_message.reply_text("\n".join(lines))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat:
        await context.application.bot_data["db"].bump_user(chat.id)
    msg = update.effective_message
    if msg and msg.text:
        await msg.reply_text(msg.text)

async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return
    await update.effective_message.reply_text(f"Ваш chat_id: {chat.id}")
