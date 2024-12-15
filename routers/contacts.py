from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import get_db, User, Contact, Tag, Group, Prompt, Organization
from utils.auth import get_current_user
from schemas.contacts_schema import (
    ContactModel, ContactUpdateModel,
    TagModel, TagUpdateModel,
    GroupModel, GroupUpdateModel,
    PromptModel
)
from fastapi.responses import JSONResponse
from typing import List

router = APIRouter(
    prefix="/api/contacts"
)

# Contact endpoints
@router.post('/create')
async def create_contact(
    data: ContactModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify organization exists and user has access
    org = db.query(Organization).filter(
        Organization.id == data.org_id,
        Organization.members.any(id=current_user.id)
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied"
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
        is_favorite=data.is_favorite
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

@router.get('/list')
async def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get contacts from organizations where user is a member
    contacts = db.query(Contact).join(
        Organization,
        Contact.org_id == Organization.id
    ).filter(
        Organization.members.any(id=current_user.id)
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
        Contact.id == contact_id,
        Organization.members.any(id=current_user.id)
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
        Contact.id == contact_id,
        Organization.members.any(id=current_user.id)
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

@router.get('/tags/list')
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tags = db.query(Tag).all()
    return tags

@router.patch('/tags/edit/{tag_id}')
async def update_tag(
    tag_id: int,
    data: TagUpdateModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(tag, field, value)
    
    try:
        db.commit()
        db.refresh(tag)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Tag updated successfully'},
        status_code=status.HTTP_200_OK
    )

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

@router.get('/groups/list')
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    groups = db.query(Group).all()
    return groups

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

# Prompt endpoints
@router.post('/prompts/create/{contact_id}')
async def create_prompt(
    contact_id: int,
    data: PromptModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    
    new_prompt = Prompt(
        thread_id=contact.thread_id,
        input_text=data.input_text,
        response_text=data.response_text,
        response_image=data.response_image
    )
    
    db.add(new_prompt)
    try:
        db.commit()
        db.refresh(new_prompt)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {'detail': 'Prompt created successfully'},
        status_code=status.HTTP_201_CREATED
    )

@router.get('/prompts/list/{contact_id}')
async def list_prompts(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prompts = db.query(Prompt).join(
        Contact
    ).join(
        Organization
    ).filter(
        Contact.id == contact_id,
        Organization.members.any(id=current_user.id)
    ).all()
    
    return prompts