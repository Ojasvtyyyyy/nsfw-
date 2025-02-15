import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from craiyon import Craiyon  # ✅ Use correct Craiyon class

# Load Telegram Bot Token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ✅ Initialize Craiyon API
generator = Craiyon()  # Uses Craiyon's online API (no GPU needed)

# ✅ Initialize Telegram Bot
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

# ✅ Flask App for Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!", 200

# ✅ Start Everything Properly with asyncio
async def main():
    """Run both Flask and Telegram Bot in a proper event loop."""
    # Start Telegram Bot in a background task
    task = asyncio.create_task(telegram_app.run_polling())

    # Start Flask in the same event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.to_thread(flask_app.run, host="0.0.0.0", port=int(os.getenv("PORT", 8080))))

    # Keep running
    await task

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Correct way to run asyncio code
