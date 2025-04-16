from telegram import Update
from telegram.ext import ContextTypes

# Diccionario en memoria; para producción usa SQLite o Redis
sessions = {}  # { telegram_user_id: expire_timestamp }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args  # Lista de strings tras `/start `
    if args:
        token = args[0]
        # TODO: validar token con tu base de datos de pagos
        if validar_token(token, user_id):
            expire = datetime.utcnow() + timedelta(minutes=5)
            sessions[user_id] = expire
            await update.message.reply_text(
                "¡Tu consulta comienza ahora! Tienes 5 min para preguntar. 😊"
            )
            return
        else:
            await update.message.reply_text("Token inválido o ya usado. Por favor, paga de nuevo.")
            return
    # Si no hay args, indica cómo empezar
    await update.message.reply_text(
        "Para iniciar la consulta, realiza el pago en la web y pulsa el botón que te llevará aquí."
    )
