import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from generate import generate_image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message."""
    update.message.reply_text("Welcome! Use /imagine <prompt> to generate an image.")

def imagine(update: Update, context: CallbackContext) -> None:
    """Handles the /imagine command."""
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("Usage: /imagine <your prompt>")
        return

    update.message.reply_text(f"Generating image for: {prompt}...")

    image_path = generate_image(prompt)
    if image_path:
        update.message.reply_photo(photo=open(image_path, "rb"))
    else:
        update.message.reply_text("Error generating image. Try again.")

def main():
    """Starts the bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("imagine", imagine))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()