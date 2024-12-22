from fastapi import APIRouter,Request
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
import httpx
 
 
load_dotenv()
 
router = APIRouter(
    prefix=""
)
 
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
version = os.getenv("VERSION")
PORT = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
 
@router.post("/webhook")
async def webhook(request: Request):
    # Log incoming messages
    body = await request.json()
    print("Incoming webhook message:", body)
 
    # Check if the webhook request contains a message
    message = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]
 
    # Check if the incoming message contains text
    if message.get("type") == "text":
        # Extract the business number to send the reply from it
        business_phone_number_id = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("metadata", {}).get("phone_number_id")
 
        # Send a reply message
        reply_data = {
            "messaging_product": "whatsapp",
            "to": message["from"],
            "text": {"body": "Echo: " + message["text"]["body"]},
            "context": {
                "message_id": message["id"],  # Shows the message as a reply to the original user message
            },
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://graph.facebook.com/{version}/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                json=reply_data
            )
 
        # Mark incoming message as read
        read_data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message["id"],
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://graph.facebook.com/{version}/{business_phone_number_id}/messages",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                json=read_data
            )
 
    return PlainTextResponse('', status_code=200)
 
@router.get("/webhook")
def verify_webhook():
    mode = Request.args.get("hub.mode")
    token = Request.args.get("hub.verify_token")
    challenge = Request.args.get("hub.challenge")
 
    # Check the mode and token sent are correct
    if mode == "subscribe" and token == VERIFY_TOKEN:
        # Respond with 200 OK and challenge token from the request
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        # Respond with '403 Forbidden' if verify tokens do not match
        return '', 403