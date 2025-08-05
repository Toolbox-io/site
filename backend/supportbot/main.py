import os
import asyncio
import aiohttp
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://main:8000")
SUPPORT_API_URL = f"{API_BASE_URL}/api/support/chat"

class SupportBot:
    def __init__(self):
        self.session_id_counter = 0
    
    def get_session_id(self, user_id: int) -> str:
        """Generate a unique session ID for each user"""
        return f"telegram-{user_id}-{self.session_id_counter}"
    
    async def send_message_to_api(self, message: str, session_id: str) -> str:
        """Send message to the support API and return the response"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    SUPPORT_API_URL,
                    json={
                        "message": message,
                        "session_id": session_id
                    },
                    headers={"Content-Type": "application/json"},
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
        await update.message.reply_text(help_message, parse_mode='HTML')

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
        
        # Send message to API
        response = await self.send_message_to_api(message_text, session_id)
        response = response.replace(".", "\\.").replace("-", "\\-")
        
        # Send response back to user
        await update.message.reply_markdown_v2(response)

    async def handle_unsupported(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unsupported message types (files, photos, etc.)"""
        await update.message.reply_text("Извините, я не поддерживаю этот файл.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        print(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            print(update)
            await update.effective_message.reply_text(
                "Произошла ошибка. Попробуйте еще раз позже."
            )

def main():
    """Main function to run the bot"""
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set")
        return
    
    # Create bot instance
    bot = SupportBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(MessageHandler(~filters.TEXT, bot.handle_unsupported))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    print("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()