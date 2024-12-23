import json
from dotenv import load_dotenv
import os
import requests
 
load_dotenv()
 
token = os.getenv("ACCESS_TOKEN")
version = os.getenv("VERSION")
number_id = os.getenv("PHONE_NUMBER_ID")
 
 
def send_txt_msg(user_contact_number: str, output: str):
    url = f"https://graph.facebook.com/{version}/{number_id}/messages"
 
    headers = {
        "Authorization" : f"Bearer {token}",
        "Content-type": "application/json"
    }
 
    data = {
        "messaging_product": "whatsapp",    
        "recipient_type": "individual",
        "to": user_contact_number,
        "type": "text",
 
        "text": {
            "body": output # use body to send msgs 
        }
    }
    print(user_contact_number)
    response = requests.post(url=url, headers=headers, json=data)
    print(response.json())
    return response
 
 
def send_img(user_contact_number: str): #JPG.JPEG,PNG
    url = f"https://graph.facebook.com/{version}/{number_id}/messages"
 
    headers = {
        "Authorization" : f"Bearer {token}",
        "Content-type": "application/json"
    }
 
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": user_contact_number,
        "type": "image",
 
        "image": {
            "link": "https://i.imgur.com/N7Mlq38.jpeg", # use links of images to send ###
            "caption": "Testing images"  ###
        }
    }
 
    response = requests.post(url=url, headers=headers, json=data)
    return response
 