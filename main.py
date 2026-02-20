import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
OLLAMA_PROXY_URL = os.getenv("OLLAMA_PROXY_URL")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")

def send_message_to_facebook(recipient_id: str, message_text: str):
    """
    Sends a message back to the user via the Meta Graph API.
    """
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={META_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully sent message to {recipient_id}")
    except requests.exceptions.HTTPError as e:
        print(f"Error sending message to Facebook: {e.response.text}")

def get_ollama_response(user_message: str) -> str:
    """
    Forwards the user's message to the local Ollama instance (via Cloudflare Tunnel).
    """
    if not OLLAMA_PROXY_URL:
        return "System Error: OLLAMA_PROXY_URL is not configured."

    # The standard Ollama chat API endpoint
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
        return "I'm sorry, I cannot reach my brain right now. Please try again later."


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Facebook Messenger Bot Webhook Server is running."}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Meta uses this endpoint to verify that you own this server.
    They will send a GET request with your META_VERIFY_TOKEN.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == META_VERIFY_TOKEN:
            print("Webhook verified successfully!")
            # Note: Meta requires a plain text response of just the challenge string
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            raise HTTPException(status_code=403, detail="Verification failed")
    
    raise HTTPException(status_code=400, detail="Missing parameters")


@app.post("/webhook")
async def handle_messages(request: Request):
    """
    Meta will POST all incoming messages from users to this endpoint.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Make sure this is a page subscription
    if body.get("object") == "page":
        # There may be multiple entries if batched
        for entry in body.get("entry", []):
            # There may be multiple messaging events
            for messaging_event in entry.get("messaging", []):
                
                # Check if this is a standard message (not a delivery receipt or read receipt)
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    
                    print(f"Received message from {sender_id}: {message_text}")
                    
                    # 1. Forward the text to Ollama
                    ai_reply = get_ollama_response(message_text)
                    
                    # 2. Send the AI's reply back to the user on Messenger
                    send_message_to_facebook(sender_id, ai_reply)

        # Meta expects a 200 OK response within 20 seconds to confirm receipt of the webhook.
        return PlainTextResponse(content="EVENT_RECEIVED", status_code=200)

    # Return a '404 Not Found' if event is not from a page subscription
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    # Make sure we bind to 0.0.0.0 so the external PaaS (Render, Heroku, etc.) can expose it
    uvicorn.run(app, host="0.0.0.0", port=8000)
