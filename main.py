from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")  # Asegúrate de tener la variable de entorno configurada

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy RUFFI, tu asistente virtual.")

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))

    # Webhook settings
    port = int(os.environ.get("PORT", 8443))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url="https://webhook.inmigrantex.online",  # Aquí se conecta con tu subdominio
    )

if __name__ == '__main__':
    main()
