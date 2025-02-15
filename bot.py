import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from craiyon import CraiyonV3  # Use Craiyon v3

# Load Telegram Bot Token from Render environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ✅ Initialize Craiyon v3 API
generator = CraiyonV3()  # Uses Craiyon's online API (no GPU needed)

# ✅ Initialize Telegram Bot
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text("Hello! Send me a prompt, and I'll generate an image for you.")

async def generate_image(update: Update, context):
    """Generate an image from user prompt using Craiyon API."""
    prompt = update.message.text
    await update.message.reply_text(f"Generating image for: '{prompt}'... Please wait ⏳")

    try:
        # Generate image using Craiyon v3
        result = generator.generate(prompt)
        image_path = "image.png"
        result.images[0].save(image_path)  # Save first generated image

        # Send image back to user
        await update.message.reply_photo(photo=open(image_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# ✅ Add command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

# ✅ Start bot
print("Bot is running...")
app.run_polling()
