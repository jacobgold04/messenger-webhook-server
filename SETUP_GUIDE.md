# Messenger Bot Setup Guide

This guide will walk you through deploying your webhook server, securely exposing your local AI, and connecting it to Facebook Messenger.

## Step 1: Push Your Code to GitHub
We need the webhook code online so a cloud service can run it for free.
1. Go to [GitHub](https://github.com/) and create a new private repository called `messenger-webhook-server`.
2. Open your VS Code terminal in `C:\Users\jtgol\OneDrive\Desktop\Random\LLM Training\Messenger Bot`.
3. Run these commands:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/messenger-webhook-server.git
   git push -u origin main
   ```

## Step 2: Deploy to Render (For Free)
Render will host your FastAPI webhook server 24/7.
1. Go to [Render](https://render.com/) and create an account.
2. Click **New** -> **Web Service**.
3. Connect your GitHub account and select your `messenger-webhook-server` repository.
4. Fill out the settings:
   - **Name:** messenger-bot-webhook (or whatever you'd like)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Instance Type:** Free
5. Click **Advanced**, then **Add Environment Variable**. Add a variable with the following name but you can choose **ANY** value you want (e.g. `jacob_secret_token_123`).
   - Key: `META_VERIFY_TOKEN`
   - Value: `YOUR_CUSTOM_SECRET_STRING_HERE`
6. Click **Create Web Service**. Wait for it to build and deploy.
7. Once it's live, copy the public URL Render gives you (e.g., `https://messenger-bot-webhook.onrender.com`). *Keep this tab open.*

## Step 3: Securely Expose Local Ollama (Ngrok Permanent Tunnel)
We need a permanent public URL that forwards messages safely into your local PC's Ollama instance, starting automatically when your PC boots.
1. Go to [Ngrok](https://ngrok.com/), create a free account, and log in.
2. In the Ngrok Dashboard, go to **Domains** on the left menu, and click **Create Domain** (this claims your one free static domain). 
   - Note down the domain it gives you (e.g., `upward-marmot-pleasing.ngrok-free.app`).
3. We will configure Ngrok to run as a silent background Windows Service to forward this domain to Ollama directly from our chat! Just follow my next instructions there.
4. Once we have the domain configured, go back to your **Render Web Service -> Environment**. Add/edit your environment variable:
   - Key: `OLLAMA_PROXY_URL`
   - Value: `https://YOUR_DOMAIN_HERE` *(Make sure to include https:// but DO NOT add `/api/chat` to the end!)*
6. Add one more environment variable for your model name:
   - Key: `OLLAMA_MODEL_NAME`
   - Value: `llama3` *(Or whatever you named your fine-tuned Unsloth model!)*
7. Render will restart your app automatically.

## Step 4: Configure Meta Developer App
Now we connect Facebook to your Render Webhook.
1. Go to [Meta for Developers](https://developers.facebook.com/).
2. Click **Create App** -> **Other** -> **Business** -> Fill in the details.
3. In the App Dashboard, scroll down to "Add products to your app" and click **Set up** on **Messenger**.
4. Under "Access Tokens", link your Facebook Page. Once linked, click **Generate Token**. 
   - **Copy this long Access Token.**
5. Go *back to Render -> Environment Dashboard* and add your final variable:
   - Key: `META_ACCESS_TOKEN`
   - Value: `PASTE_THE_LONG_META_TOKEN_HERE`
6. Once Render restarts, go *back to the Meta Developer Dashboard*.
7. Scroll down to the **Webhooks** section under Messenger settings. Click **Add Callback URL**.
   - **Callback URL:** `https://your-render-url-here.onrender.com/webhook` (Make sure `/webhook` is at the end!)
   - **Verify Token:** Paste the custom string you created in Step 2 (`jacob_secret_token_123`).
8. Click **Verify and Save**. (If this fails, check the "Logs" tab on Render to see the error).
9. Once saved, click **Manage** next to the webhook and Subscribe to the `messages` event.

### 🎉 You're Done!
You can now go to Facebook Messenger and send a message to your Page! It will send the request to Render, which forwards it to Cloudflare, which hits the Ollama `.gguf` running on your PC's GPU!
