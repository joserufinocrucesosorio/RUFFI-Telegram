import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Instancia de Flask
app = Flask(__name__)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola, soy RUFFI. ¿En qué puedo ayudarte hoy?")

# Manejo de mensajes normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    chat_id = update.message.chat_id

    if "residencia" in text:
        respuesta = "Para renovar tu residencia temporal, visita: https://sede.administracionespublicas.gob.es"
    else:
        respuesta = "Recibido. Pronto te daré más información."

    await context.bot.send_message(chat_id=chat_id, text=respuesta)

# Main
def main():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Ejecutar bot en modo webhook
    PORT = int(os.environ.get("PORT", 8443))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://ruffi-telegram-production-2760.up.railway.app/webhook"
    )

if __name__ == "__main__":
    main()
