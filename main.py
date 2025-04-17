import os
import logging
from datetime import datetime, timedelta

import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─── Configuración básica ───────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY     = os.getenv("OPENAI_KEY")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL", "https://webhook.inmigrantex.online/webhook")

openai.api_key = OPENAI_KEY

# Sesiones temporales de 5 minutos tras pago
sessions: dict[int, datetime] = {}

# ─── Handlers ───────────────────────────────────────────────────────────────────

async def token_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /start <token> : inicia la sesión si el token es válido """
    user_id = update.effective_user.id
    args = context.args

    if args:
        token = args[0]
        # Aquí valida tu token contra la base de datos de pagos
        if validar_token(token, user_id):
            expires = datetime.utcnow() + timedelta(minutes=5)
            sessions[user_id] = expires
            await update.message.reply_text(
                "✅ Sesión iniciada. Tienes **5 min** para tu consulta."
            )
        else:
            await update.message.reply_text(
                "❌ Token inválido o ya usado. Por favor, paga de nuevo."
            )
    else:
        await update.message.reply_text(
            "Para empezar, paga en la web y pulsa el botón de Telegram."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Responde a cada mensaje comprobando primero el tiempo de sesión """
    user_id = update.effective_user.id
    now = datetime.utcnow()
    expires = sessions.get(user_id)

    if not expires or now > expires:
        return await update.message.reply_text(
            "⏰ Tu tiempo expiró. Vuelve a pagar en:\nhttps://inmigrantex.online"
        )

    prompt = update.message.text
    # Llamada a OpenAI
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        reply_text = resp.choices[0].message.content
    except Exception as e:
        logging.error("OpenAI error: %s", e)
        reply_text = "Lo siento, no pude procesar tu petición."

    # Enviar texto
    await update.message.reply_text(reply_text)

    # TODO: aquí podrías generar voz (por ejemplo con ElevenLabs)
    # y enviarla con `await update.message.reply_voice(voice=bytes_audio)`

# ─── Función de validación de token (placeholder) ───────────────────────────────

def validar_token(token: str, user_id: int) -> bool:
    """
    Comprueba en tu base de datos que el token es válido y pertenece a este usuario.
    Devuelve True una sola vez; marca el token como usado.
    """
    # Aquí tu lógica: consulta SQL, Redis, etc.
    return True  # para pruebas iniciales

# ─── Configuración y arranque del bot en modo webhook ───────────────────────────

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", token_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Registra el webhook en Telegram
    app.bot.set_webhook(WEBHOOK_URL)

    # Inicia el servidor webhook
    port = int(os.environ.get("PORT", "8443"))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
