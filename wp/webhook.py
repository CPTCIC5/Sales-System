from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
import httpx
from sqlalchemy.orm import Session
from ai.app import chat_with_assistant
from schemas.contacts_schema import PrompCreatetModel
from db.models import get_db, Contact, Organization, Prompt  # Import your models

load_dotenv()

router = APIRouter(
    prefix=""
)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
version = os.getenv("VERSION")
PORT = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print("Incoming webhook message:", body)

    message = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]

    if message.get("type") == "text":
        business_phone_number_id = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("metadata", {}).get("phone_number_id")
        message_text = str(message["text"]["body"])
        sender_phone = message["from"]

        try:
            # Look up contact by phone number
            contact = db.query(Contact).filter(Contact.phone_number == sender_phone).first()
            if not contact:
                return PlainTextResponse('', status_code=200)

            # Create prompt model
            prompt = PrompCreatetModel(
                input_text=message_text
            )

            # Call chat_with_assistant with correct IDs
            assistant_response = await chat_with_assistant(
                user_input=prompt,
                contact_id=contact.id,
                org_id=contact.org_id,
                db=db
            )
            print(assistant_response) 
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return PlainTextResponse('', status_code=200)

            # Send reply message
        reply_data = {
                "messaging_product": "whatsapp",
                "to": sender_phone,
                "text": {"body": assistant_response},  # Replace with assistant_response
                "context": {
                    "message_id": message["id"],  # Shows the message as a reply to the original user message
                },
            }
        print(reply_data)
        async with httpx.AsyncClient() as client: # not posting the reply data
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
