from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.services.group_code import generate_group_code
from app.models.groups import Group
from app.models.memberships import Membership
from app.extension import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg2 import errors
from sqlalchemy import select

router = APIRouter()

@router.post('/groups')
async def admin_creates_code(request: Request, db: AsyncSession = Depends(get_db)):
    user_id =  request.id #get user id to make admin
    name    =  request.name #group name

    if not name or not user_id:
        return JSONResponse(content={'error':'Group Name Missing'}, status_code=400)
    
    invite_code = generate_group_code()

    try:
        group = Group(
            name=name,
            created_by=user_id,
            invite_code=invite_code,
        )
        db.add(group)
        await db.commit()

    except errors.UniqueViolation:
        invite_code = generate_group_code()
        db.add(group)
        await db.commit()

@router.get('/group/me')
async def all_user_groups(requests: Request, db : AsyncSession =  Depends(get_db())):
    user_id =  requests.id

    user = (await db.execute(select(Membership).where(Membership.user_id == user_id))).scalars().all()
    json_user = [
        {
            "joined_at": user.joined_at,
            "name":user.group_name,
        } 
        for user in user
    ]

    return JSONResponse(content=json_user, status_code=200)

