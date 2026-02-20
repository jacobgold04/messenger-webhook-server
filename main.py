import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")

def get_ollama_response(user_message: str) -> str:
    """
    Forwards the user's message to the local Ollama instance on this PC.
    """
    endpoint = f"{OLLAMA_PROXY_URL.rstrip('/')}/api/chat"
    
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False # Wait for the full response to finish before returning
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120) 
        response.raise_for_status()
        data = response.json()
        
        # Extract the bot's reply from the Ollama response
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        else:
            print(f"Unexpected JSON from Ollama: {data}")
            return "Error: Could not parse response from the AI model."

    except requests.exceptions.RequestException as e:
        print(f"Error querying Ollama API: {e}")
        return "I'm sorry, my local Ollama server is unreachable or turned off."


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fired every time the bot receives a text message in Telegram.
    """
    # Exclude edits or system messages
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_id = update.message.chat_id
    user_name = update.effective_user.first_name

    print(f"Received message in chat {chat_id} from {user_name}: {user_text}")

    # Forward the text to local Ollama
    ai_reply = get_ollama_response(user_text)

    # Send the AI's reply back to the Telegram chat
    await update.message.reply_text(ai_reply)

def main() -> None:
    """
    Start the Telegram bot.
    """
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN is missing from your .env file!")
        return
        
    print("Starting Telegram Bot... (Press CTRL+C to stop)")
    print(f"Connecting to Ollama at {OLLAMA_PROXY_URL}")

    # Create the Telegram Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Listen for ANY text message (excluding commands that start with /)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Start the Bot (Long Polling)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
