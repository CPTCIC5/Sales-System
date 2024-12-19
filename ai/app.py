from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json
from pydantic import BaseModel

class LeadQualificationModel(BaseModel):
    qualification_score: int = 0
    budget_confirmed: bool = False
    authority_confirmed: bool = False
    need_confirmed: bool = False
    timeline_confirmed: bool = False
    meeting_readiness: bool = False
    
class ContactModel(BaseModel):
    name: str 
    org_id: int
    phone_number: str
    website_url: str = None
    industry: str = None
    thread_id: str = None
    qualification: LeadQualificationModel = LeadQualificationModel()

load_dotenv()

client= OpenAI()

# Store the assistant ID for future use

def get_meeting_link():
    return "https://outlook.office.com/bookwithme/user/8ef8abcb1a04480ab07f1f7165fbfd2f%40salesgenio.ai?anonymous&isanonymous=true"


def safe_execute_tool(func_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely execute tool functions with error handling and logging
    """
    try:
        if func_name == "get_meeting_link":
            result = get_meeting_link()
        
        return result
    except Exception as e:
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
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"error": "Internal processing error"})
            })
    
    return tool_outputs


def chat_with_assistant(user_input: str, user: ContactModel, vspace_id= "vs_rjNKWuoxeD0ruMxAhsuBTor2"):
    # Evaluate meeting readiness before processing message
    meeting_ready = evaluate_meeting_readiness(user, user_input)
    
    if meeting_ready:
        # Add meeting suggestion to context
        user_input += "\n\nNote: Lead is qualified for meeting. You can share meeting link if appropriate."
    
    print(f"Processing message from {user.name}")
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
        
        # Add the context as the initial message with enhanced details
        context = f"""
        You're speaking with {user.name} from the {user.industry if user.industry else 'Not provided'} industry
        Company Website: {user.website_url if user.website_url else 'Not provided'}
        Contact Number: {user.phone_number}
        Organization ID: {user.org_id}

        Your Role:
        - Act as a professional sales representative
        - Build rapport and understand their business needs
        - Keep messages concise and engaging (2-3 sentences max)
        - Use friendly, professional language with occasional emojis
        - Ask targeted questions about their business challenges
        - Listen actively and show genuine interest
        - Guide naturally through discovery → solution → value proposition
        - Focus on understanding their pain points
        - Never reveal you're AI or mention being an assistant
        - Maintain a warm, consultative tone throughout

        Key Objectives:
        1. Understand their business needs
        2. Identify pain points and challenges
        3. Build trust through meaningful conversation
        4. Guide towards scheduling a meeting when appropriate

        
        Lead Qualification Process:
        1. Understand Budget:
           - Ask about current spending on similar solutions
           - Explore budget allocation for new solutions
        
        2. Verify Authority:
           - Identify their role in decision-making
           - Understand the buying process
        
        3. Confirm Need:
           - Identify specific pain points
           - Understand current solutions/processes
           - Quantify the impact of their challenges
        
        4. Establish Timeline:
           - Determine urgency of the need
           - Understand their implementation timeline
        
        Meeting Link Sharing Criteria:
        - Share meeting link ONLY when:
            1. Lead shows clear interest
            2. At least 3 qualification criteria are met
            3. They specifically ask about next steps
            4. You've identified concrete pain points
        
        Remember to:
        - Keep track of qualification status
        - Don't rush to share the meeting link
        - Focus on value before pushing for a meeting
        """
        
        # Send enhanced context for new threads
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=context,
        )
    
    # Add the user message
    message = client.beta.threads.messages.create(
        thread_id=user.thread_id,
        role="user",
        content=user_input,
    )

    # Run the assistant with error handling
    try:
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
                print(f"Run failed with status: {run.status}")
                return "I apologize, but I'm having trouble processing your request. Could you please rephrase that?"
                
            # Wait before polling again with exponential backoff
            import time
            time.sleep(1)

    except Exception as e:
        print(f"Error in chat_with_assistant: {str(e)}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."

def evaluate_meeting_readiness(user: ContactModel, message_content: str) -> bool:
    qualification = user.qualification
    
    # Update qualification based on message content
    if "budget" in message_content.lower():
        qualification.budget_confirmed = True
    if "decision" in message_content.lower():
        qualification.authority_confirmed = True
    if "problem" in message_content.lower() or "challenge" in message_content.lower():
        qualification.need_confirmed = True
    if "timeline" in message_content.lower() or "when" in message_content.lower():
        qualification.timeline_confirmed = True
    
    # Calculate qualification score
    score = sum([
        qualification.budget_confirmed,
        qualification.authority_confirmed,
        qualification.need_confirmed,
        qualification.timeline_confirmed
    ]) * 25  # Each criterion is worth 25 points
    
    qualification.qualification_score = score
    
    # Determine meeting readiness
    qualification.meeting_readiness = (
        score >= 75 and  # At least 3 criteria met
        qualification.need_confirmed  # Must have confirmed need
    )
    
    return qualification.meeting_readiness

# Main interaction loop
if __name__ == "__main__":
    print("Sales Assistant (Type 'quit' to exit)")
    print("---------------------------------------------------")
    
    # Create a test lead for the main loop
    test_lead = ContactModel(
        name="Sarthak Jain",
        org_id=1,
        phone_number="+1234567890"
    )
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        response = chat_with_assistant(user_input, test_lead)
        print(f"\nAssistant: {response}")