import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Claves desde variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy *RUFFI*, tu asistente virtual para temas de inmigración en España 🇪🇸.\n\n"
        "Puedes preguntarme lo que necesites, y te responderé con gusto 😊.",
        parse_mode="Markdown"
    )

# Manejo general de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.effective_chat.id

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Responde como un asistente especializado en inmigración en España, con tono profesional, confiable y empático."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response.choices[0].message.content
        await context.bot.send_message(chat_id=chat_id, text=answer)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Ha ocurrido un error procesando tu consulta.")
        print("Error:", e)

# Iniciar la app con webhook
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN no está definido.")
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY no está definido.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    PORT = int(os.environ.get("PORT", 8443))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://inmigrantex.online/webhook"
    )

if __name__ == "__main__":
    main()
