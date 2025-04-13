import os
import requests
from pytube import YouTube
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
@app.route('/')
def health_check():
    return "🤖 Bot YouTube Online - Wellington"

def get_main_menu():
    return ReplyKeyboardMarkup(
        [['📽️ Baixar Vídeo YouTube'], ['❔ Ajuda']],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        """📽️ *Baixador de Vídeos do YouTube*

Envie um link do YouTube que eu baixo e te envio de volta.

🔧 Criado por: Wellington""",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        """📘 *Como usar?*

1. Envie um link do YouTube.
2. Eu vou baixar e te enviar o vídeo.

Simples assim!""",
        parse_mode="Markdown"
    )

def baixar_youtube_video(link):
    try:
        api_url = "https://youloader.app/api/button"
        response = requests.post(api_url, json={"url": link}, timeout=15).json()

        # Pega o primeiro link MP4 disponível (geralmente 720p ou 360p)
        for video in response.get("video", []):
            if "mp4" in video.get("type", ""):
                return video["url"]
        return None
    except Exception as e:
        print(f"❌ Erro ao baixar vídeo: {e}")
        return None


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    if text == '📽️ Baixar Vídeo YouTube':
        update.message.reply_text("📤 Envie o link do YouTube:")
    elif text == '❔ Ajuda':
        help_command(update, context)
    elif "youtube.com" in text or "youtu.be" in text:
    update.message.reply_text("⏳ Processando vídeo do YouTube...")
    video_url = baixar_youtube_video(text)
    if video_url:
        update.message.reply_video(video_url, caption="✅ Aqui está seu vídeo!", reply_markup=get_main_menu())
    else:
        update.message.reply_text("❌ Não consegui baixar. Tente outro link ou verifique o formato.")

    else:
        update.message.reply_text("⚠️ Link inválido. Envie um link do YouTube.")

def main():
    Thread(target=lambda: app.run(host='0.0.0.0', port=PORT)).start()
    updater = Updater(TOKEN, use_context=True)
    updater.bot.delete_webhook(drop_pending_updates=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ajuda", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🚀 Bot YouTube iniciado com sucesso!")
    updater.start_polling(drop_pending_updates=True)
    updater.idle()

if __name__ == "__main__":
    main()
