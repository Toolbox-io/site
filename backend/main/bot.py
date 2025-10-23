import os
import asyncio
import aiohttp
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SUPPORT_API_URL = f"{API_BASE_URL}/api/support/chat"
INTERNAL_BOT_TOKEN = os.getenv("INTERNAL_BOT_TOKEN")

logger = logging.getLogger(__name__)

class SupportBot:
    def __init__(self):
        self.session_id_counter = 0
        self.application = None
    
    def get_session_id(self, user_id: int) -> str:
        """Generate a unique session ID for each user"""
        return f"telegram-{user_id}-{self.session_id_counter}"
    
    async def send_message_to_api(self, message: str, session_id: str, user_id: int = None) -> str:
        """Send message to the support API and return the response"""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {"Content-Type": "application/json"}
                if user_id is not None and INTERNAL_BOT_TOKEN:
                    headers["X-User-ID"] = str(user_id)
                    headers["X-Internal-Token"] = INTERNAL_BOT_TOKEN
                async with session.post(
                    SUPPORT_API_URL,
                    json={
                        "message": message,
                        "session_id": session_id
                    },
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 429:
                        return "Ваш лимит запросов исчерпан. Попробуйте еще раз завтра."
                    
                    if response.status != 200:
                        return f"Ошибка сервера: {response.status}"
                    
                    # Read the streaming response and accumulate content
                    full_response = ""
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                if 'content' in data:
                                    full_response += data['content']
                                elif 'error' in data:
                                    return f"Ошибка: {data['error']}"
                            except json.JSONDecodeError:
                                continue
                    
                    return full_response if full_response else "Извините, не удалось получить ответ."
                    
            except asyncio.TimeoutError:
                return "Превышено время ожидания ответа. Попробуйте еще раз."
            except Exception as e:
                return f"Ошибка соединения: {str(e)}"

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "Привет! Я ассистент Toolbox.io! 🤖\n\n"
            "Помогу с установкой, использованием и настройкой приложения.\n"
            "Просто напишите ваш вопрос, и я постараюсь помочь!\n\n"
            "Ассистент работает на базе ИИ, возможны неточности."
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🔧 <b>Доступные команды:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n\n"
            "💡 <b>Как использовать:</b>\n"
            "Просто отправьте текстовое сообщение с вашим вопросом, "
            "и я постараюсь на него ответить.\n\n"
            "⚠️ <b>Ограничения:</b>\n"
            "• Поддерживаются только текстовые сообщения\n"
            "• Максимальная длина сообщения: 1024 символа\n"
            "• Лимит: 1 запрос в секунду, 20 запросов в день"
        )
        await update.message.reply_html(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check message length
        if len(message_text) > 1024:
            await update.message.reply_text(
                "Сообщение слишком длинное. Максимальная длина: 1024 символа."
            )
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        # Get session ID for this user
        session_id = self.get_session_id(user_id)
        
        # Send message to API with user_id for rate limiting
        response = await self.send_message_to_api(message_text, session_id, user_id=user_id)
        response = response.replace(".", "\\.").replace("-", "\\-").replace("!", "\\!")
        
        # Send response back to user
        await update.message.reply_markdown_v2(response)

    async def handle_unsupported(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unsupported message types (files, photos, etc.)"""
        await update.message.reply_text("Извините, я не поддерживаю этот файл.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Попробуйте еще раз позже."
            )

    async def start_bot(self):
        """Start the Telegram bot"""
        if not TELEGRAM_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not set - support bot will not start")
            return
        
        logger.info("Starting Toolbox.io support bot...")
        
        # Create application
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(~filters.TEXT, self.handle_unsupported))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        # Start the bot
        logger.info("Bot is running")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application:
            logger.info("Stopping support bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

# Global bot instance
bot_instance = None

async def start_support_bot():
    """Start the support bot as a background task"""
    global bot_instance
    bot_instance = SupportBot()
    await bot_instance.start_bot()

async def stop_support_bot():
    """Stop the support bot"""
    global bot_instance
    if bot_instance:
        await bot_instance.stop_bot()
