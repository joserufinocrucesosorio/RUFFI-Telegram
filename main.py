"""
RUFFI – bot de Telegram con pago por sesión de 5 min
Versión PTB 20.8 – 17 abr 2025
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict

import openai
import stripe
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─── Config ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY      = os.getenv("OPENAI_KEY")
STRIPE_SECRET   = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_URL     = os.getenv(
    "WEBHOOK_URL",
    "https://ruffi-telegram-production-c936.up.railway.app/webhook",
)

openai.api_key  = OPENAI_KEY
stripe.api_key  = STRIPE_SECRET

sessions: Dict[int, datetime] = {}        # user_id → expiry UTC

# ─── Stripe helper ─────────────────────────────────────────────────────────────
def validar_token(session_id: str, tg_user_id: int) -> bool:
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            return False
        # TODO: marcar session_id como usado por tg_user_id en BD
        return True
    except Exception as exc:
        logging.error("Stripe error: %s", exc)
        return False

# ─── Handlers ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if args and validar_token(args[0], user_id):
        sessions[user_id] = datetime.utcnow() + timedelta(minutes=5)
        await update.message.reply_text(
            "✅ Pago confirmado. ¡Tienes 5 min para tu consulta!"
        )
    else:
        await update.message.reply_text(
            "🔗 Primero paga en https://inmigrantex.online y luego toca el botón que te llevará aquí."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expires = sessions.get(user_id)

    if not expires or datetime.utcnow() > expires:
        return await update.message.reply_text(
            "⏰ Tu tiempo expiró. Vuelve a pagar en https://inmigrantex.online"
        )

    prompt = update.message.text
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        answer = resp.choices[0].message.content
    except Exception as exc:
        logging.error("OpenAI error: %s", exc)
        answer = "Lo siento, hubo un problema al procesar tu pregunta."

    await update.message.reply_text(answer)

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Falta TELEGRAM_TOKEN en variables de entorno")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    port = int(os.getenv("PORT", "8443"))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
