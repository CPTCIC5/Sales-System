from fastapi import APIRouter

router= APIRouter(
    prefix="/api/auth"
)

@router.get("/login")
async def login():
    return {"Hello": "fr3re3ferfer"}