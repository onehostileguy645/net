import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Store chat sessions per user
user_chats = {}


def get_or_create_chat(user_id):
    """Get existing chat or create new one for user"""
    if user_id not in user_chats:
        user_chats[user_id] = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="You're Net, a friendly and caring companion. You're supportive, playful, and give natural, conversational responses. Keep responses short and human-like, like texting a close friend.",
            ),
        )
    return user_chats[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "Hey! It's Net 💕\n"
        "I'm here for you! Just send me a message and let's chat.\n\n"
        "Commands:\n"
        "/start - Start chatting\n"
        "/reset - Start fresh conversation\n"
        "/help - Show this message"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset conversation"""
    user_id = update.effective_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await update.message.reply_text("Okay! Fresh start 🌟 What's up?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "Just talk to me naturally! I'm here to chat.\n\n"
        "Commands:\n"
        "/start - Start chatting\n"
        "/reset - Start fresh conversation\n"
        "/help - Show this message"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user_id = update.effective_user.id
    user_message = update.message.text

    try:
        # Get or create chat for this user
        chat = get_or_create_chat(user_id)

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Get response from Gemini
        response = chat.send_message(user_message)

        # Send response
        await update.message.reply_text(response.text.strip())

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(
            "Oops, something went wrong 😅 Try again?"
        )


def main():
    """Start the bot"""
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()