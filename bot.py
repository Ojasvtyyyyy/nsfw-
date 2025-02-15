import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from craiyon import Craiyon  # ✅ Use correct Craiyon class

# Load Telegram Bot Token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ✅ Initialize Craiyon API
generator = Craiyon()  # Uses Craiyon's online API (no GPU needed)

# ✅ Initialize Flask (for Render Free Tier)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

# ✅ Telegram Bot Logic
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text("Hello! Send me a prompt, and I'll generate an image for you.")

async def generate_image(update: Update, context):
    """Generate an image from user prompt using Craiyon API."""
    prompt = update.message.text
    await update.message.reply_text(f"Generating image for: '{prompt}'... Please wait ⏳")

    try:
        # Generate image using Craiyon
        result = generator.generate(prompt, negative_prompt="bad quality", model_type="art")
        image_path = "generated/image_0.png"
        result.save_images()  # Save the generated image

        # Send image back to user
        await update.message.reply_photo(photo=open(image_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# ✅ Add command handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

# ✅ Run Telegram Bot in a separate thread
def run_telegram_bot():
    print("Starting Telegram bot...")
    telegram_app.run_polling()

threading.Thread(target=run_telegram_bot, daemon=True).start()

# ✅ Start Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
