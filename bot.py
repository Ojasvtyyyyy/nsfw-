import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from craiyon import Craiyon
from threading import Thread
import json
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

# Initialize Telegram Bot
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text("Hello! Send me a prompt, and I'll generate an image for you.")

async def generate_image(update: Update, context):
    """Generate an image from user prompt using Craiyon API."""
    prompt = update.message.text
    await update.message.reply_text(f"Generating image for: '{prompt}'... Please wait ⏳")
    
    try:
        # Add more detailed logging
        logger.info(f"Attempting to generate image with prompt: {prompt}")
        
        # Generate image with error catching
        try:
            result = generator.generate(prompt, negative_prompt="bad quality", model_type="art")
            logger.info("Image generation successful")
        except Exception as e:
            logger.error(f"Error during image generation: {str(e)}")
            await update.message.reply_text("Sorry, there was an error generating the image. Please try again.")
            return

        # Create the generated directory if it doesn't exist
        os.makedirs("generated", exist_ok=True)
        
        # Save and send image with error catching
        try:
            image_path = "generated/image_0.png"
            result.save_images()
            logger.info(f"Image saved to {image_path}")
            
            # Check if file exists before sending
            if os.path.exists(image_path):
                await update.message.reply_photo(photo=open(image_path, "rb"))
                logger.info("Image sent successfully")
            else:
                raise FileNotFoundError(f"Generated image not found at {image_path}")
                
        except Exception as e:
            logger.error(f"Error saving or sending image: {str(e)}")
            await update.message.reply_text("Sorry, there was an error processing the generated image.")
            return
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

# Add command handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

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
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Run Telegram bot
    telegram_app.run_polling()

if __name__ == "__main__":
    main()
