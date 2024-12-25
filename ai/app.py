from fastapi import APIRouter, Depends, HTTPException
from db.models import get_db
from utils.auth import get_current_user
from sqlalchemy.orm import Session
from db.models import User, Organization, Prompt, Contact
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import json
from pydantic import BaseModel
from schemas.contacts_schema import PrompCreatetModel
from wp.send_msg_imgs import send_txt_msg
from utils.auth import get_organization_products

router= APIRouter(
    prefix="/api/prompt"
)

class LeadQualificationModel(BaseModel):
    qualification_score: int = 0
    budget_confirmed: bool = False
    authority_confirmed: bool = False
    need_confirmed: bool = False
    timeline_confirmed: bool = False
    meeting_readiness: bool = False
    detected_type: str = None  # "B2B", "B2C", or None
    

load_dotenv()
client= OpenAI()

# Store the assistant ID for future use

def get_meeting_link(org_meeting_url: str = None):
    """Get meeting link for the organization"""
    if not org_meeting_url:
        return {"error": "No meeting URL configured"}
    return {"meeting_url": org_meeting_url}


def safe_execute_tool(func_name: str, arguments: Dict[str, Any], org_id: int = None, org_meeting_url: str = None) -> Optional[Dict[str, Any]]:
    """
    Safely execute tool functions with error handling and logging
    """
    try:
        if func_name == "get_meeting_link":
            result = get_meeting_link(org_meeting_url)
        elif func_name == "get_organization_products":
            # Use the org_id passed from the route
            if not org_id:
                return {"error": "org_id is required"}
            # Get DB session
            db = next(get_db())
            result = get_organization_products(org_id=org_id, db=db)
            # Convert SQLAlchemy objects to dictionaries for JSON serialization
            if isinstance(result, list):
                result = [
                    {
                        "products": [{"id": p.id, "title": p.title, "description": p.description, 
                                    "price": p.price_per_quantity, "currency": p.currency} 
                                   for p in result[0]],
                        "external_data": result[1] if len(result) > 1 else None
                    }
                ]
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

@router.post('/{org_id}/create/{contact_id}')
def chat_with_assistant(user_input: PrompCreatetModel, contact_id: int, org_id: int, db: Session = Depends(get_db)):
    try:
        prospect = db.query(Contact).filter(Contact.id == contact_id).first()
        if not prospect:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        organization = db.query(Organization).filter(Organization.id == org_id).first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Create qualification model instance
        qualification = LeadQualificationModel()
        
        # Evaluate meeting readiness before processing message
        meeting_ready = evaluate_meeting_readiness(qualification, user_input.input_text)
        if meeting_ready:
            user_input.input_text += "\n\nNote: Lead is qualified for meeting. You can share meeting link if appropriate."

        print(f"Processing message from {prospect.name}")
        assistant_id= organization.assistant_id

        has_no_prompts = db.query(Prompt).filter(Prompt.contact_id == prospect.id).count() == 0
        print(has_no_prompts)
        if has_no_prompts:
            print('efewewfewf')
            context = get_context_template(prospect)
            
            message = client.beta.threads.messages.create(
                thread_id=prospect.thread_id,
                role="assistant",
                content=context,
            )
        
        # Add the user message
        message = client.beta.threads.messages.create(
            thread_id=prospect.thread_id,
            role="user",
            content=user_input.input_text,
        )

        # Run the assistant with error handling
        try:
            run = client.beta.threads.runs.create(
                thread_id=prospect.thread_id,
                assistant_id=assistant_id,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_organization_products",
                            "description": "Get products for the current organization",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_meeting_link",
                            "description": "Get the organization's meeting link",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    }
                ]
            )

            while True:
                run = client.beta.threads.runs.retrieve(
                    thread_id=prospect.thread_id,
                    run_id=run.id
                )

                if run.status == "requires_action":
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        # Pass both org_id and meeting_url
                        result = safe_execute_tool(
                            function_name, 
                            {}, 
                            org_id=org_id,
                            org_meeting_url=organization.meeting_url
                        )
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=prospect.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

                elif run.status == "completed":
                    # Get the assistant's response
                    messages = client.beta.threads.messages.list(
                        thread_id=prospect.thread_id,
                        order="desc",
                        limit=1
                    )
                    assistant_response = messages.data[0].content[0].text.value
                    send_txt_msg(prospect.phone_number, assistant_response)
                    # Store both the prompt and response in database
                    new_prompt = Prompt(
                        organization_id=organization.id,
                        contact_id=prospect.id,
                        input_text=user_input.input_text,
                        response_text=assistant_response
                    )
                    db.add(new_prompt)
                    db.commit()

                    return assistant_response
                
                elif run.status in ["failed", "cancelled", "expired"]:
                    print(f"Run failed with status: {run.status}")
                    return "I apologize, but I'm having trouble processing your request. Could you please rephrase that?"
                    
                # Wait before polling again with exponential backoff
                import time
                time.sleep(1)

        except Exception as e:
            print(f"Error in chat_with_assistant: {str(e)}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
        
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def analyze_qualification_criteria(message_content: str) -> Dict[str, Any]:
    """Analyzes message content to detect BANT criteria and other qualification signals"""
    
    function_json = {
        "name": "analyze_qualification",
        "description": "Analyze message content for sales qualification criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "budget_confirmed": {
                    "type": "boolean",
                    "description": "Message indicates budget discussion or financial capacity"
                },
                "authority_confirmed": {
                    "type": "boolean",
                    "description": "Message indicates decision-making authority or involvement"
                },
                "need_confirmed": {
                    "type": "boolean",
                    "description": "Message indicates clear business need or pain points"
                },
                "timeline_confirmed": {
                    "type": "boolean",
                    "description": "Message indicates implementation timeline or urgency"
                },
                "reasoning": {
                    "type": "object",
                    "properties": {
                        "budget": {"type": "string"},
                        "authority": {"type": "string"},
                        "need": {"type": "string"},
                        "timeline": {"type": "string"}
                    },
                    "description": "Reasoning for each criterion detection"
                }
            },
            "required": ["budget_confirmed", "authority_confirmed", "need_confirmed", "timeline_confirmed", "reasoning"]
        }
    }

    messages = [
        {"role": "system", "content": "You are a sales qualification expert. Analyze the message for BANT criteria."},
        {"role": "user", "content": message_content}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=[function_json],
        function_call={"name": "analyze_qualification"}
    )

    result = json.loads(response.choices[0].message.function_call.arguments)
    return result

def evaluate_meeting_readiness(user: LeadQualificationModel, message_content: str) -> bool:
    qualification = user
    
    # Use AI to analyze the message content
    analysis = analyze_qualification_criteria(message_content)
    
    # Update qualification based on AI analysis
    qualification.budget_confirmed = qualification.budget_confirmed or analysis['budget_confirmed']
    qualification.authority_confirmed = qualification.authority_confirmed or analysis['authority_confirmed']
    qualification.need_confirmed = qualification.need_confirmed or analysis['need_confirmed']
    qualification.timeline_confirmed = qualification.timeline_confirmed or analysis['timeline_confirmed']
    
    # Calculate qualification score
    score = sum([
        qualification.budget_confirmed,
        qualification.authority_confirmed,
        qualification.need_confirmed,
        qualification.timeline_confirmed
    ]) * 25  # Each criterion is worth 25 points
    
    qualification.qualification_score = score
    
    # Determine meeting readiness - require need confirmation and at least 2 other criteria
    qualification.meeting_readiness = (
        score >= 75 and  # At least 3 criteria met
        qualification.need_confirmed  # Must have confirmed need
    )
    
    return qualification.meeting_readiness

def get_context_template(contact: Contact) -> str:
    """Generate context template based on business model and contact information"""
    base_context = f"""
    You're speaking with {contact.name}
    Contact Number: {contact.phone_number if contact.phone_number else 'Not provided'}
    """

    return base_context