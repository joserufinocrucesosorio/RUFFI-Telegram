import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy *RUFFI*, tu asistente virtual sobre inmigración en España 🇪🇸.\n\n"
        "Puedes preguntarme sobre trámites, residencia, nacionalidad, etc. Estoy aquí para ayudarte.",
        parse_mode='Markdown'
    )

# Manejo de mensajes de texto normales
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.effective_chat.id

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Responde como un experto en inmigración en España, con tono profesional, claro y empático."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
        await context.bot.send_message(chat_id=chat_id, text=reply)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Lo siento, ha ocurrido un error interno.")
        print("Error al procesar mensaje:", e)

# Función principal
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN no está definido. Verifica tus variables de entorno en Railway.")
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY no está definido. Verifica tus variables de entorno en Railway.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Webhook con dominio propio
    PORT = int(os.environ.get("PORT", 8443))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://inmigrantex.online/webhook"
    )

if __name__ == "__main__":
    main()
