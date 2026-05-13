from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import groups, memberships
from app.extension import get_db
from sqlalchemy import select
from app.services.group_code import generate_group_code
from psycopg2 import errors

router = APIRouter()

@router.post('/groups/join')
async def join(request: Request, db: AsyncSession = Depends(get_db())):
    invite_code = request.get('invite_code')
    if not invite_code:
        return JSONResponse(content={'error':'No invite code provided'}, status_code=400)
    
    existing_code = (await db.execute(select(groups.Group).where(groups.Group.invite_code==invite_code))).scalar_one_or_none()

    if not existing_code:
        return JSONResponse(content={'error':'Code Not Found'}, status_code=404)
    
    new_member = memberships.Membership(
        user_id = request.get('id'),
        group_id = existing_code.id,
        group_name = existing_code.name,
    )

    db.add(new_member)
    await db.commit()

    return JSONResponse(content={'ok':'success'}, status_code=200)

@router.post('/groups/{group_id}/regenerate-invite')
async def regen_invite(request: Request, db: AsyncSession = Depends(get_db())):
    new_code = generate_group_code()
    old_code =  request.get('invite_code')  

    while True:
        code_check = (await db.execute(
            select(groups.Group).where(groups.Group.invite_code==new_code)
        )).scalar_one_or_none()

        if not code_check:
            break
        new_code = generate_group_code()
    
    groups.Group(
        (await db.execute(
            select(groups.Group).where(groups.Group.invite_code==old_code)
        )).scalar_one_or_none()
    )

    await db.commit()

    return JSONResponse(content={'message':f'{new_code}'},status_code=200)

@router.delete('/groups/{group_id}/members/{user_id}')
async def remove_member(request: Request, db: AsyncSession = Depends(get_db())):
    member_id = request.get('id')
    group_id = request.get('group_id')
    if not member_id:
        return JSONResponse(content={'error':'User Not Found'}, status_code=404)
    
    to_be_deleted = (await db.execute(
        select(memberships.Membership)
        .where(memberships.Membership.user_id==member_id and memberships.Membership.group_id==group_id))
        ).scalar_one_or_none()
    
    await db.delete(to_be_deleted)

    return JSONResponse(content={'ok':200},status_code=200)