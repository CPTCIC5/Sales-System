from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import requests

load_dotenv()



app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
version = os.getenv("VERSION")
PORT = os.getenv("PORT", 5000)  # Default to 5000 if PORT is not set

@app.route("/webhook", methods=["POST"])
def webhook():
    # Log incoming messages
    print("Incoming webhook message:", request.json)

    # Check if the webhook request contains a message
    message = request.json.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0]

    # Check if the incoming message contains text
    if message.get("type") == "text":
        # Extract the business number to send the reply from it
        business_phone_number_id = request.json.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("metadata", {}).get("phone_number_id")

        # Send a reply message
        reply_data = {
            "messaging_product": "whatsapp",
            "to": message["from"],
            "text": {"body": "Echo: " + message["text"]["body"]},
            "context": {
                "message_id": message["id"],  # Shows the message as a reply to the original user message
            },
        }
        requests.post(
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
        requests.post(
            f"https://graph.facebook.com/{version}/{business_phone_number_id}/messages",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json=read_data
        )

    return '', 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # Check the mode and token sent are correct
    if mode == "subscribe" and token == VERIFY_TOKEN:
        # Respond with 200 OK and challenge token from the request
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        # Respond with '403 Forbidden' if verify tokens do not match
        return '', 403


if __name__ == "__main__":
    app.run(port=int(PORT))




###========= SEND MESSAGE TEMPLATE

# def send_whatsapp_message():
#     url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": "Bearer " + ACCESS_TOKEN,
#         "Content-Type": "application/json",
#     }
#     data = {
#         "messaging_product": "whatsapp",
#         "to": RECIPIENT_WAID,
#         "type": "template",
#         "template": {"name": "hello_world", "language": {"code": "en_US"}},
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response

# response = send_whatsapp_message()
# print(response.status_code)
# print(response.json())

# def get_text_message_input(recipient, text):
#     return json.dumps(
#         {
#             "messaging_product": "whatsapp",
#             "recipient_type": "individual",
#             "to": recipient,
#             "type": "text",
#             "text": {"preview_url": False, "body": text},
#         }
#     )


# def send_message(data):
#     headers = {
#         "Content-type": "application/json",
#         "Authorization": f"Bearer {ACCESS_TOKEN}",
#     }

#     url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

#     response = requests.post(url, data=data, headers=headers)
#     if response.status_code == 200:
#         print("Status:", response.status_code)
#         print("Content-type:", response.headers["content-type"])
#         print("Body:", response.text)
#         return response
#     else:
#         print(response.status_code)
#         print(response.text)
#         return response


# data = get_text_message_input(
#     recipient=RECIPIENT_WAID, text="Hello, this is a test message."
# )

# response = send_message(data)