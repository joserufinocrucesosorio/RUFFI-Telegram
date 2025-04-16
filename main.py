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

# Configuración de logging (opcional para ver logs)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Claves de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Instancia de Flask (opcional, en esta versión no la usamos directamente)
app = Flask(__name__)

# Función para /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola, soy RUFFI. ¿En qué puedo ayudarte hoy?")

# Función para mensajes normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat.id
    # Respuesta automática básica (puedes mejorar con IA)
    if "residencia" in text.lower():
        reply = "Para renovar tu residencia temporal, visita la sede electrónica de extranjería: https://sede.administracionespublicas.gob.es"
    else:
        reply = "Recibido. Pronto te daré más información."
    await context.bot.send_message(chat_id=chat_id, text=reply)

# Función principal
def main():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app_bot.add_handler(CommandHandler("start", start))

    # Mensajes normales que no son comandos
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook directo en Railway
    PORT = int(os.environ.get("PORT", 8443))
    app_bot.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://railway.com/project/9e8cc375-ce76-433f-a18e-e6adfc541b70/service/1b642220-a8f7-4e08-b084-9708f632e6b0?environmentId=7393bd99-30b6-484b-88a3-0e13a4bde7ae&id=a5d5b04a-b3d6-4c02-921a-8f131665f82f#deploy"
    )

if __name__ == "__main__":
    main()
