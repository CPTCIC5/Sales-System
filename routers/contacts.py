from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import get_db, User, Contact, Tag, Group, Prompt, Organization
from utils.auth import get_current_user
from schemas.contacts_schema import (
    ContactModel, ContactUpdateModel,
    TagModel,
    GroupModel, GroupUpdateModel,
    PrompCreatetModel
)
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client= OpenAI()
router = APIRouter(
    prefix="/api/contacts"
)

@router.get('/{contact_id}')
async def get_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    paginated_contact= db.query(Contact).filter(Contact.id == contact_id).first()
    return paginated_contact


# Contact endpoints
@router.post('/create')
async def create_contact(
    data: ContactModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's organization (similar to organizations.py)
    users_org = db.query(Organization).filter(Organization.root_user == current_user).first()
    if not users_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Verify the org_id matches the user's organization
    if users_org.id != data.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    # Check if phone number already exists in this organization
    if data.phone_number:
        existing_contact = db.query(Contact).filter(
            Contact.org_id == data.org_id,
            Contact.phone_number == data.phone_number
        ).first()
        
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists in this organization"
            )

    # Update thread with organization settings
    if data.thread_id:
        try:
            client.beta.threads.update(
                thread_id=data.thread_id,
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [users_org.vspace_id]
                    }
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update thread settings: {str(e)}"
            )

    new_contact = Contact(
        org_id=data.org_id,
        name=data.name,
        phone_number=data.phone_number,
        industry=data.industry,
        website_url=data.website_url,
        avatar=data.avatar,
        utm_campaign=data.utm_campaign,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        is_favorite=data.is_favorite,
        thread_id=data.thread_id
    )
    
    db.add(new_contact)
    try:
        db.commit()
        db.refresh(new_contact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Contact created successfully'},
        status_code=status.HTTP_201_CREATED
    )

@router.get('/')
async def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's organization
    users_org = db.query(Organization).filter(Organization.root_user == current_user).first()
    if not users_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get contacts for this organization
    contacts = db.query(Contact).filter(
        Contact.org_id == users_org.id
    ).all()
    
    return contacts

@router.patch('/edit/{contact_id}')
async def update_contact(
    contact_id: int,
    data: ContactUpdateModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).join(
        Organization
    ).filter(
        Contact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied"
        )
    
    # Update only provided fields
    for field, value in data.dict(exclude_unset=True).items():
        setattr(contact, field, value)
    
    try:
        db.commit()
        db.refresh(contact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Contact updated successfully'},
        status_code=status.HTTP_200_OK
    )

@router.delete('/delete/{contact_id}')
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).join(
        Organization
    ).filter(
        Contact.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied"
        )
    
    db.delete(contact)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Contact deleted successfully'},
        status_code=status.HTTP_204_NO_CONTENT
    )


####
@router.get('/groups')
async def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    #groups= db.query(Group).all()
    #print(groups)
    return JSONResponse(status_code=status.HTTP_200_OK)


# Tag endpoints
@router.post('/tags/create')
async def create_tag(
    data: TagModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_tag = Tag(
        tag_name=data.tag_name,
        color_code=data.color_code
    )
    
    db.add(new_tag)
    try:
        db.commit()
        db.refresh(new_tag)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Tag created successfully'},
        status_code=status.HTTP_201_CREATED
    )

@router.get('/tags')
async def list_tags(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    return {"fewwfe": "fe3ffe3"}

@router.delete('/tags/delete/{tag_id}')
async def delete_tag(tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tag= db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
        return JSONResponse({"detail": "Tag deleted successfully"}, status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

# Group endpoints
@router.post('/groups/create')
async def create_group(
    data: GroupModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_group = Group(name=data.name)
    
    db.add(new_group)
    try:
        db.commit()
        db.refresh(new_group)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Group created successfully'},
        status_code=status.HTTP_201_CREATED
    )



@router.get('/groups/{group_id}')
async def paginated_group(group_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group= db.query(Group).filter(Group.id == group_id).first()
    if group:
        return group.contacts
    return HTTPException(detail="Not found", status_code=status.HTTP_404_NOT_FOUND)


@router.post('/tags/{contact_id}/assign/{tag_id}')
async def assign_tag(
    contact_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get contact and verify access
    contact = db.query(Contact).join(
        Organization
    ).filter(
        Contact.id == contact_id,
        Organization.members.any(id=current_user.id)
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied"
        )

    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Add tag to contact if not already assigned
    if tag not in contact.tags:
        contact.tags.append(tag)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        {'detail': 'Tag assigned successfully'},
        status_code=status.HTTP_200_OK
    )


@router.patch('/groups/edit/{group_id}')
async def update_group(
    group_id: int,
    data: GroupUpdateModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    group.name = data.name
    
    try:
        db.commit()
        db.refresh(group)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Group updated successfully'},
        status_code=status.HTTP_200_OK
    )

@router.post('/groups/{contact_id}/assign/{group_id}')
async def assign_group(
    contact_id: int,
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get contact and verify access
    contact = db.query(Contact).join(
        Organization
    ).filter(
        Contact.id == contact_id,
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found or access denied"
        )

    # Get group
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )

    # Add contact to group if not already assigned
    if contact not in group.contacts:
        group.contacts.append(contact)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        {'detail': 'Contact assigned to group successfully'},
        status_code=status.HTTP_200_OK
    )

@router.delete('/groups/{group_id}')
async def group_delete(group_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    group= db.query(Group).filter(Group.id == group_id).first()
    if group:
        db.delete(group)
        db.commit()
        return JSONResponse({'detail': "Group deleted"}, status_code=status.HTTP_204_NO_CONTENT)
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND)