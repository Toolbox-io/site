#!/usr/bin/env python3
"""
Toolbox.io Support Assistant
Standalone Telegram bot for user support
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add the main backend to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "main"))

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file from project root (three levels up from backend/assistant)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Disable HTTP request logs
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure logging for the assistant
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Load context and instructions
try:
    with open("context/data.md", "r", encoding="utf-8") as f:
        full_context = f.read()
except FileNotFoundError:
    logger.error("context/data.md not found.")
    sys.exit(1)

try:
    with open("context/instruction.md", "r", encoding="utf-8") as f:
        instructions = f.read()
except FileNotFoundError:
    logger.error("context/instruction.md not found.")
    sys.exit(1)

# Import bot functionality
from bot import start_support_bot, stop_support_bot
from ai_model import initialize_ai_model

async def main():
    """Main entry point for the support assistant"""
    logger.info("Starting Toolbox.io Support Assistant...")
    
    # Check if Telegram bot token is configured
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("TELEGRAM_BOT_TOKEN not configured. Exiting.")
        sys.exit(1)
    
    try:
        # Initialize AI model
        logger.info("Initializing AI model...")
        initialize_ai_model(full_context, instructions)
        
        # Start the support bot
        await start_support_bot()
        
        # Keep the bot running
        logger.info("Support Assistant is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping Support Assistant...")
        await stop_support_bot()
        logger.info("Support Assistant stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Support Assistant stopped by user")
    except Exception as e:
        logger.error(f"Support Assistant error: {e}")
        sys.exit(1)
