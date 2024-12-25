from fastapi import APIRouter,Request,HTTPException,Response
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
async def webhook(request: Request, input_prompt: str):
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
            "text": {"body": input_prompt},
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
async def verify_webhook(request: Request):
    # Get query parameters from the request
    query_params = request.query_params
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")

    # Check the mode and token sent are correct
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return PlainTextResponse(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch.")
