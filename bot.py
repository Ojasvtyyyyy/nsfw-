import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from craiyon import Craiyon
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Telegram Bot Token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Craiyon API
generator = Craiyon()

# Initialize Telegram Bot with specific settings to prevent conflicts
telegram_app = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .arbitrary_callback_data(True)
    .build()
)

# Add a flag to track if the bot is running
bot_running = False
bot_lock = threading.Lock()

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text("Hello! Send me a prompt, and I'll generate an image for you.")

async def generate_image(update: Update, context):
    """Generate an image from user prompt using Craiyon API."""
    prompt = update.message.text
    await update.message.reply_text(f"Generating image for: '{prompt}'... Please wait ⏳")
    
    try:
        logger.info(f"Attempting to generate image with prompt: {prompt}")
        result = generator.generate(prompt, negative_prompt="bad quality", model_type="art")
        
        os.makedirs("generated", exist_ok=True)
        image_path = "generated/image_0.png"
        result.save_images()
        
        if os.path.exists(image_path):
            await update.message.reply_photo(photo=open(image_path, "rb"))
            logger.info("Image sent successfully")
        else:
            raise FileNotFoundError(f"Generated image not found at {image_path}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Sorry, an error occurred: {str(e)}")

# Flask App
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    """Run Flask in a separate thread"""
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def main():
    """Run both Flask and Telegram Bot"""
    global bot_running
    
    with bot_lock:
        if bot_running:
            logger.warning("Bot is already running!")
            return
        bot_running = True
    
    try:
        # Add handlers
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))
        
        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True  # This ensures the thread will be terminated when the main program exits
        flask_thread.start()
        
        # Start the bot with specific settings
        telegram_app.run_polling(
            drop_pending_updates=True,  # Ignore any pending updates
            allowed_updates=Update.ALL_TYPES,
            stop_signals=None  # Disable default signal handlers
        )
    finally:
        with bot_lock:
            bot_running = False

if __name__ == "__main__":
    main()
