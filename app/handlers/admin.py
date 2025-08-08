from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes
import logging, asyncio

log = logging.getLogger(__name__)

def _is_admin(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    admins = set(context.application.bot_data.get("admins", []))
    return user_id in admins

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not _is_admin(context, user.id):
        return
    users, msgs = await context.application.bot_data["db"].stats()
    await update.effective_message.reply_text(f"👥 Пользователей: {users}\n✉️ Сообщений: {msgs}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not _is_admin(context, user.id):
        return
    if not context.args:
        await update.effective_message.reply_text("Использование: /broadcast <текст>")
        return
    text = " ".join(context.args)

    # Читаем все chat_id из БД
    db = context.application.bot_data["db"]
    if not db.pool:
        await update.effective_message.reply_text("БД не настроена, рассылка недоступна.")
        return

    sent = 0
    async with db.pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT chat_id FROM users;")
            rows = await cur.fetchall()
            chat_ids = [int(r[0]) for r in rows]

    # Шлем по партиям, чтобы не упереться в лимиты
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id, text)
            sent += 1
            await asyncio.sleep(0.06)  # ~16 msg/sec
        except Exception as e:
            log.warning("broadcast fail chat_id=%s: %s", chat_id, e)

    await update.effective_message.reply_text(f"Рассылка завершена. Успешно: {sent}/{len(chat_ids)}")
