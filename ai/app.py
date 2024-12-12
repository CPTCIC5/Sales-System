from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json
from pydantic import BaseModel


class ContactCreate(BaseModel):
    org_id: int
    name: str
    phone_number: str = None
    industry: str = None
    website_url: str = None
    utm_campaign: str = None
    utm_source: str = None
    utm_medium: str = None
    thread_id: str= None
# Create logs directory if it doesn't exist
logs_dir= Path("logs")
logs_dir.mkdir(exist_ok=True)

# Update logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=logs_dir / f'sales_assistant_{datetime.now().strftime("%Y%m%d")}.log'
)

load_dotenv()

client= OpenAI()

# Store the assistant ID for future use

def get_meeting_link():
    #"""This function is used to fetch meeting link of the requested/associated organization via it's org_id (organization_id)"""
    print('fn-call-01')
    return "https://outlook.office.com/bookwithme/user/8ef8abcb1a04480ab07f1f7165fbfd2f%40salesgenio.ai?anonymous&isanonymous=true"


def safe_execute_tool(func_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely execute tool functions with error handling and logging
    """
    try:
        logging.info(f"Executing {func_name} with arguments: {arguments}")
        if func_name == "get_meeting_link":
            result = get_meeting_link()
        
        logging.info(f"Successfully executed {func_name}: {result}")
        return result
    except Exception as e:
        logging.error(f"Error executing {func_name}: {str(e)}", exc_info=True)
        return {"error": str(e)}
    

def handle_tool_calls(tool_calls):
    """Handle tool calls from the assistant with error handling"""
    tool_outputs = []
    
    for tool_call in tool_calls:
        try:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = safe_execute_tool(function_name, arguments)
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result)
            })
        except Exception as e:
            logging.error(f"Tool call handling error: {str(e)}", exc_info=True)
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"error": "Internal processing error"})
            })
    
    return tool_outputs


def chat_with_assistant(user_input: str, user: ContactCreate, vspace_id= "vs_rjNKWuoxeD0ruMxAhsuBTor2"):
    print(user.name)
    assistant_id = "asst_P22hVD8Pa82ylwFv6tuTU6Co"

    if user.thread_id is None:
        # Create a new thread if the lead doesn't have one
        thread = client.beta.threads.create(
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vspace_id]
                }
            }
        )
        user.thread_id = thread.id
        print(f"Created new thread with ID: {thread.id}")
        
        # Add the context as the initial message
        context = f"""
        You're speaking with {user.name}
        Their business is in the {user.industry} industry
        Website: {user.website_url}

        Remember:
        - Keep messages short and conversational
        - Use friendly language and appropriate emojis
        - Ask questions to keep the conversation flowing
        - Guide through the sales framework naturally
        - Never reveal you're AI
        """
        
        # Send context only for new threads
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=context,
        )
    
    # Add the actual user message
    message = client.beta.threads.messages.create(
        thread_id=user.thread_id,
        role="user",
        content=user_input,
    )
    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=user.thread_id,
        assistant_id=assistant_id
    )

    # Poll for completion or handle required actions
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=user.thread_id,
            run_id=run.id
        )

        if run.status == "completed":
            # Get the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=user.thread_id,
                order="desc",
                limit=1
            )
            return messages.data[0].content[0].text.value
        
        elif run.status == "requires_action":
            tool_outputs = handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=user.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status in ["failed", "cancelled", "expired"]:
            return f"Error: Run ended with status {run.status}"
            
        # Wait before polling again
        import time
        time.sleep(1)

# Main interaction loop
if __name__ == "__main__":
    print("Sales Assistant (Type 'quit' to exit)")
    print("---------------------------------------------------")
    
    # Create a test lead for the main loop
    test_lead = ContactCreate(
        name="Dany Alvarez",
        org_id=1,
        phone_number="+1234567890",
        website_url="https://danyalvarez.co",
        industry="ecommerce"
    )
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        response = chat_with_assistant(user_input, test_lead)
        print(f"\nAssistant: {response}")