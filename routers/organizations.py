from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from db.models import get_db,User,Organization,OrganizationInvite, OrganizationKeys, OrganizationFileSystem
from utils.auth import get_current_user
from schemas.organizations_schema import OrganizationCreateModel, OrganizationInviteCreateModel
from fastapi.responses import JSONResponse
router= APIRouter(
    prefix="/api/organizations"
)

@router.post('/create')
async def create_org(data: OrganizationCreateModel, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    x1= db.query(Organization).filter(Organization.root_user_id == data.root_user_id).first()
    if x1 is None:
        new_org= Organization(
            root_user_id= current_user.id,
            business_name= data.business_name,
            business_webURL= data.business_webURL,
            industry_type= data.business_webURL
        )
        db.add(new_org)
        try:
            db.commit()
            db.refresh(new_org)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

        # Create OrganizationKeys
        org_data = OrganizationKeys(organization_id=new_org.id)
        # Create OrganizationFileSystem
        org_filesystem = OrganizationFileSystem(org_id=new_org.id)
        
        db.add_all([org_data, org_filesystem])
        try:
            db.commit()
            db.refresh(org_data)
            db.refresh(org_filesystem)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
            
        return JSONResponse({'detail': 'New Organization created'}, status_code=status.HTTP_201_CREATED)
    return HTTPException(status_code=status.HTTP_226_IM_USED, detail="One User can only own only 1 organization, create new account")


@router.post('/invite')
async def organization_invite(
    invite_data: OrganizationInviteCreateModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(current_user.organizations)
    users_org= db.query(Organization).filter(Organization.root_user == current_user).first()
    # Check if organization exists and current user is the root user
    org = db.query(Organization).filter(Organization.id == users_org.id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if org.root_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can send invites"
        )
    
    # Check if invite already exists for this email
    existing_invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.organization_id == users_org.id,
        OrganizationInvite.email == invite_data.email
    ).first()
    
    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already exists for this email"
        )
    
    # Create new invite
    new_invite = OrganizationInvite(
        organization_id=users_org.id,
        email=invite_data.email,
        invite_code=invite_data.invite_code,
        accepted=False
    )
    
    db.add(new_invite)
    try:
        db.commit()
        db.refresh(new_invite)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        {
            'detail': 'Invitation sent successfully',
            'invite_code': new_invite.invite_code
        },
        status_code=status.HTTP_201_CREATED
    )