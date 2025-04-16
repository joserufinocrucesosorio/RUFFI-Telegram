import os
import logging
from datetime import datetime, timedelta

import openai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY     = os.getenv("OPENAI_KEY")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL", "https://webhook.inmigrantex.online/webhook")

openai.api_key = OPENAI_KEY

sessions: dict[int, datetime] = {}

async def token_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if args and validar_token(args[0], user_id):
        sessions[user_id] = datetime.utcnow() + timedelta(minutes=5)
        await update.message.reply_text("✅ Sesión iniciada: 5 min de consulta.")
    else:
        await update.message.reply_text(
            "🔗 Paga en la web y pulsa el botón de Telegram para empezar."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    expires = sessions.get(user_id)
    if not expires or datetime.utcnow() > expires:
        return await update.message.reply_text(
            "⏰ Tiempo expirado. Vuelve a pagar en https://inmigrantex.online"
        )

    prompt = update.message.text
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.choices[0].message.content
    except Exception as e:
        logging.error("OpenAI error: %s", e)
        text = "Lo siento, no pude procesar tu petición."

    await update.message.reply_text(text)
    # Aquí podrías añadir TTS con ElevenLabs y mandar voice

def validar_token(token: str, user_id: int) -> bool:
    # TODO: lógica real de verificación y marcado de token como usado
    return True

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", token_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    port = int(os.environ.get("PORT", "8443"))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
