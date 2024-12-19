from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json
from pydantic import BaseModel
from schemas.organizations_schema import Organization

class LeadQualificationModel(BaseModel):
    qualification_score: int = 0
    budget_confirmed: bool = False
    authority_confirmed: bool = False
    need_confirmed: bool = False
    timeline_confirmed: bool = False
    meeting_readiness: bool = False
    detected_type: str = None  # "B2B", "B2C", or None
    
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


def chat_with_assistant(user_input: str, user: ContactModel, organization: Organization, vspace_id= "vs_rjNKWuoxeD0ruMxAhsuBTor2"):
    # Evaluate meeting readiness before processing message
    meeting_ready = evaluate_meeting_readiness(user, user_input)
    
    if meeting_ready:
        # Add meeting suggestion to context
        user_input += "\n\nNote: Lead is qualified for meeting. You can share meeting link if appropriate."
    
    print(f"Processing message from {user.name}")
    assistant_id = "asst_P22hVD8Pa82ylwFv6tuTU6Co"

    if user.thread_id is None:
        # Select appropriate context template based on organization type
        context = get_context_template(organization.business_model, user)
        
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

def get_context_template(business_model: str, user: ContactModel) -> str:
    base_context = f"""
    You're speaking with {user.name}
    Contact Number: {user.phone_number}
    """
    
    if business_model == "B2B":
        return base_context + """
        Industry: {user.industry if user.industry else 'Not provided'}
        Company Website: {user.website_url if user.website_url else 'Not provided'}
        
        Your Role:
        - Act as a professional B2B sales representative
        - Focus on business needs and pain points
        [... rest of B2B specific instructions ...]
        """
    
    elif business_model == "B2C":
        return base_context + """
        Your Role:
        - Act as a friendly customer service representative
        - Focus on individual needs and preferences
        - Keep language simple and jargon-free
        - Emphasize personal benefits
        
        Key Objectives:
        1. Understand personal needs
        2. Identify individual preferences
        3. Build personal connection
        4. Guide towards appropriate solution
        
        Qualification Process:
        1. Understand Requirements:
           - Ask about specific needs
           - Explore usage scenarios
        
        2. Confirm Decision Making:
           - Understand timeline
           - Discuss budget expectations
        
        Meeting Link Sharing Criteria:
        - Share meeting link when:
            1. Customer shows clear interest
            2. Has specific needs that require detailed discussion
            3. Requests more information
        """
    
    else:  # "BOTH"
        return base_context + """
        Your Role:
        - Adapt your approach based on the conversation
        - Start neutral and determine if speaking with business or individual
        - Adjust language and focus accordingly
        
        Initial Assessment:
        - Ask open-ended questions about their interest
        - Listen for business or personal use indicators
        - Adapt qualification process based on response
        
        Key Objectives:
        1. Identify if business or personal use
        2. Adjust communication style accordingly
        3. Follow appropriate qualification process
        """

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