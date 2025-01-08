import os
import random
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import math
import colorsys
import logging
import sys

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
# TOKEN = '7243623278:AAFwvUaGyraIQTtj-ouiwbF3EZY-1YCFLNQ'  # Hardcoded for testing
TOKEN = "7746073326:AAEVoCuTN6hfgkYbgN0Pm8KTL2qEkXetJKk"   # Kelvin's
TOKEN_ADDRESS = '6t7heUCjsgxa5ZwFQyfZwY9cEm9ACMxjgJrH1MELpump'  # Hardcoded for testing
BOT_TITLE = "ASScii art AI Agent"
BOT_SUBTITLE = "Making Tech Sexier Than Your Girlfriend! 🔥🚨🚀"
CAPTION_TEXT = """In this digital age, the real love affair is with your keyboard. 💻

> Join our Telegram community!"""
WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://sasscii.com')
TELEGRAM_URL = os.getenv('TELEGRAM_URL', 'https://t.me/sasscii')
TWITTER_URL = os.getenv('TWITTER_URL', 'https://twitter.com/sasscii')

logger.info(f"Loaded title: {BOT_TITLE}")

# Directory containing ASCII art files
ASCII_ART_DIR = 'ascii_art'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    logger.info("Received /start command")
    logger.info(f"Chat type: {update.effective_chat.type}")
    logger.info(f"Chat ID: {update.effective_chat.id}")
    try:
        await update.message.reply_text(
            'Welcome! Use /art to get random ASCII art with Solana market data.'
        )
        logger.info("Sent start message")
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}", exc_info=True)

async def art(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /art command"""
    logger.info("Received /art command")
    logger.info(f"Chat type: {update.effective_chat.type}")
    logger.info(f"Chat ID: {update.effective_chat.id}")
    logger.info(f"Message: {update.message.text if update.message else 'No message'}")
    
    try:
        # Get market data
        market_data = get_raydium_data()
        logger.info(f"Got market data: {market_data}")
        
        # Get random ASCII art
        art_files = [f for f in os.listdir(ASCII_ART_DIR) if f.endswith('.txt')]
        logger.info(f"Found art files: {art_files}")
        if not art_files:
            await update.message.reply_text("No ASCII art files found!")
            return
            
        art_file = os.path.join(ASCII_ART_DIR, random.choice(art_files))
        logger.info(f"Selected art file: {art_file}")
        with open(art_file, 'r', encoding='utf-8') as f:
            art_content = f.read()
        logger.info("Read art content")
        
        # Create and send the image
        logger.info("Creating image...")
        image = create_market_image(art_content, market_data)
        if image is None:
            logger.error("Failed to create image")
            await update.message.reply_text("Error creating image!")
            return
        logger.info("Created image")
        
        # Save image to bytes
        logger.info("Saving image to bytes...")
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        logger.info("Saved image to bytes")
        
        # Format caption with market data
        logger.info("Formatting caption...")
        caption = f"**{BOT_TITLE}**\n{BOT_SUBTITLE}\n\n{CAPTION_TEXT}\n\n"
        caption += f"💎 Market Cap: {market_data['market_cap']}\n"
        caption += f"💰 Price: {market_data['price']}\n"
        caption += f"📊 24h Volume: {market_data['volume24h']}\n\n"
        caption += f"🌐 Website: {WEBSITE_URL}\n"
        caption += f"💬 Telegram: {TELEGRAM_URL}\n"
        caption += f"🐦 Twitter: {TWITTER_URL}\n"
        logger.info("Formatted caption")
        
        # Send image with caption
        logger.info("Sending image...")
        await update.message.reply_photo(
            photo=img_byte_arr,
            caption=caption,
            parse_mode='Markdown'
        )
        logger.info("Sent image successfully")
    except Exception as e:
        logger.error(f"Error in art command", exc_info=True)
        await update.message.reply_text("Error generating ASCII art!")

def get_raydium_data():
    """Get market data from DexScreener API"""
    try:
        # Get data from DexScreener API
        url = f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"
        response = requests.get(url)
        data = response.json()
        
        # Extract price and volume from the first pair
        if data.get('pairs') and len(data['pairs']) > 0:
            pair = data['pairs'][0]
            price = pair.get('priceUsd', 'N/A')
            volume24h = pair.get('volume', {}).get('h24', 'N/A')
            liquidity = pair.get('liquidity', {}).get('usd', 'N/A')
            
            # Format values
            if price != 'N/A':
                price = f"${float(price):.4f}"
            if volume24h != 'N/A':
                volume24h = f"${int(float(volume24h)):,}"
            if liquidity != 'N/A':
                market_cap = f"${int(float(liquidity)):,}"
            else:
                market_cap = "N/A"
            
            return {
                'price': price,
                'volume24h': volume24h,
                'market_cap': market_cap
            }
    except Exception as e:
        logger.error(f"Error fetching Raydium data", exc_info=True)
    
    # Return fallback data if API fails
    return {
        'price': '$0.0001',
        'volume24h': '$50K',
        'market_cap': '$29K'
    }

def get_random_bright_color():
    """Generate a random bright color"""
    # Use HSV color space to ensure bright colors
    hue = random.random()  # Random hue
    saturation = 0.8 + random.random() * 0.2  # High saturation (0.8-1.0)
    value = 0.8 + random.random() * 0.2  # High value/brightness (0.8-1.0)
    
    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return tuple(int(x * 255) for x in rgb)

def convert_braille_to_blocks(text):
    """Convert Braille characters to solid blocks"""
    result = ""
    for char in text:
        if char == '⠀' or char.startswith('�'):  # Check for Braille space or any Braille character
            result += '█'
        else:
            result += char
    return result

def create_market_image(art_content, market_data):
    """Create an image with ASCII art and market data"""
    try:
        logger.info("Starting image creation")
        # Create a new image with black background
        WIDTH = 1200
        HEIGHT = 1800
        img = Image.new('RGB', (WIDTH, HEIGHT), color='black')
        draw = ImageDraw.Draw(img)
        
        # Generate random bright color for the entire image
        MAIN_COLOR = get_random_bright_color()
        GLOW_COLOR = tuple(int(c * 0.8) for c in MAIN_COLOR)  # Slightly dimmer for glow
        
        # Load font with fallbacks
        font_paths = [
            # "/System/Library/Fonts/Monaco.ttf",
            # "/Library/Fonts/DejaVuSansMono-Bold.ttf",
            # "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            # "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
            "./DejaVuSansMono-Bold.ttf"
        ]
        
        art_font = None
        title_font = None
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    art_font = ImageFont.truetype(font_path, 30)
                    title_font = ImageFont.truetype(font_path, 60)
                    logger.info(f"Using font: {font_path}")
                    break
            except Exception as e:
                logger.warning(f"Failed to load font {font_path}: {e}")
                continue
        
        if art_font is None or title_font is None:
            logger.info("Using default font")
            art_font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw title at the top
        title = BOT_TITLE
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (WIDTH - title_width) // 2
        title_y = 50
        
        # Draw title with glow
        for offset in range(1, 4):
            for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
                draw.text((title_x + dx, title_y + dy), title, font=title_font, fill=GLOW_COLOR)
        draw.text((title_x, title_y), title, font=title_font, fill=MAIN_COLOR)
        
        # Process ASCII art - convert Braille to blocks
        art_lines = art_content.split('\n')
        processed_lines = []
        for line in art_lines:
            if line.strip():
                processed_line = convert_braille_to_blocks(line)
                processed_lines.append(processed_line)
        
        # Calculate dimensions for a single block character
        sample_char = "█"
        char_bbox = draw.textbbox((0, 0), sample_char, font=art_font)
        char_width = char_bbox[2] - char_bbox[0]
        char_height = char_bbox[3] - char_bbox[1]
        
        # Calculate spacing
        h_spacing = 1  # Minimal spacing between blocks
        v_spacing = 1  # Minimal spacing between lines
        
        # Calculate total dimensions
        max_chars_per_line = max(len(line) for line in processed_lines)
        total_width = max_chars_per_line * (char_width + h_spacing)
        
        # Center the art
        art_x = (WIDTH - total_width) // 2
        art_y = title_y + 120
        
        # Draw each character
        for line in processed_lines:
            x = art_x
            for char in line:
                if char.strip():
                    # Create glow effect
                    glow_radius = 2
                    glow_steps = 8
                    for r in range(1, glow_radius + 1):
                        for angle in range(0, 360, int(360 / glow_steps)):
                            dx = int(r * math.cos(math.radians(angle)))
                            dy = int(r * math.sin(math.radians(angle)))
                            draw.text((x + dx, art_y + dy), char, font=art_font, fill=GLOW_COLOR)
                    draw.text((x, art_y), char, font=art_font, fill=MAIN_COLOR)
                x += char_width + h_spacing
            art_y += char_height + v_spacing
        
        return img
    except Exception as e:
        logger.error(f"Error in create_market_image", exc_info=True)
        return None


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("art", art))
    application.run_polling()







# async def main():
#     """Start the bot"""
#     # Create application
#     application = None
#     try:
#         logger.info("Creating application...")
#         application = Application.builder().token(TOKEN).build()
        
#         # Get bot username
#         logger.info("Getting bot info...")
#         bot = await application.bot.get_me()
#         bot_username = bot.username
#         logger.info(f"Bot username: {bot_username}")
        
#         # Add command handlers
#         logger.info("Adding command handlers...")
#         application.add_handler(CommandHandler("start", start))
#         application.add_handler(CommandHandler("art", art))
        
#         # Add message handler for group messages
#         application.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r'^/art(@.*)?$'), art))
        
#         # Register commands
#         logger.info("Registering commands...")
#         commands = [
#             ("start", "Start the bot"),
#             ("art", "Get random ASCII art with market data")
#         ]
#         await application.bot.set_my_commands(commands)
#         logger.info("Bot commands registered")
        
#         # Initialize the application
#         # await application.initialize()
        
#         # Start polling
#         logger.info("Starting polling...")
#         # await application.start()
#         await application.run_polling(allowed_updates=Update.ALL_TYPES)
#     except Exception as e:
#         logger.error("Error in main", exc_info=True)
#     finally:
#         if application:
#             logger.info("Shutting down...")
#             await application.stop()
#             await application.shutdown()

# if __name__ == '__main__':
#     logger.info("Starting bot script...")
#     import asyncio
#     asyncio.run(main())
#     # asyncio.get_running_loop()