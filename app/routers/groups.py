from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.group_code import generate_group_code, update_group
from app.models.groups import Group
from app.models.memberships import Membership
from app.extension import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg2 import errors
from sqlalchemy import select
from app.schema import groupPatch

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
            "description": (await db.execute(select(Group.description).where(Group.id==user.id)))
        } 
        for user in user
    ]

    return JSONResponse(content=json_user, status_code=200)

@router.patch('/groups/{group_id}')
async def update(payload: groupPatch, db: AsyncSession = Depends(get_db())):
    update_group(payload.name, payload.description)

@router.delete('/groups/{group_id}')
async def delete_group(request: Request, db : AsyncSession = Depends(get_db())):
    invite_code = request.invite_code

    to_be_deleted = (await db.execute(select(Group).where(Group.invite_code==invite_code))).scalar_one_or_none()
    if not to_be_deleted:
        raise HTTPException(status_code=404, detail="Group not found")
        
    await db.delete(to_be_deleted)