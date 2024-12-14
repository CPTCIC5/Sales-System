from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from db.models import get_db,User
from utils.auth import get_current_user
from schemas.organizations_schema import OrganizationCreateModel
from db.models import Organization
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
        return JSONResponse({'detail': 'New Organization  created'}, status_code=status.HTTP_201_CREATED)
    return HTTPException(status_code=status.HTTP_226_IM_USED, detail="One User can only own only 1 organization, create new account")


@router.post('/invite-{org_id}')
async def organization_invite(org_id: int):
    pass