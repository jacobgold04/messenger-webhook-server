# Telegram Bot Setup Guide

This guide will walk you through creating your Telegram bot and connecting it to your local Ollama instance. Because we are using Telegram, **your bot runs entirely on your PC**. You do not need to use Render, Ngrok, or any cloud services.

## Step 1: Create Your Bot on Telegram
1. Open the Telegram app on your phone or computer.
2. Search for `@BotFather` (the official Telegram bot for making bots). It will have a blue verified checkmark.
3. Tap **Start** to message it, then send the command `/newbot`.
4. It will ask for a **Name** (e.g., *Jacob's AI Bot*) and a **Username** (must end in "bot", e.g., *JacobLLMBot*).
5. Once created, BotFather will give you a long API Token that looks something like this:
   `1234567890:AAH...`
   - **Copy this Token.**

## Step 2: Configure Your Project
1. Open the `.env` file in VS Code (`C:\Users\jtgol\OneDrive\Desktop\Random\LLM Training\Messenger Bot\.env`).
2. Delete everything inside it and replace it with:
```env
TELEGRAM_BOT_TOKEN=paste_your_token_here_with_no_quotes
OLLAMA_PROXY_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3
```

## Step 3: Run the Bot!
1. Open your VS Code terminal in the `Messenger Bot` folder.
2. Activate your virtual environment: `.\venv\Scripts\Activate`
3. Install the Telegram library: `pip install -r requirements.txt`
4. Start the bot: `python main.py`

### 🎉 You're Done!
As long as that terminal window says "Starting Telegram Bot...", your bot is alive. 

Go to Telegram, search for the `@Username` you created in Step 1, and send it a message! You can also click on the bot's profile in Telegram and click **"Add to Group or Channel"** to drop it into any group chat instantly.
