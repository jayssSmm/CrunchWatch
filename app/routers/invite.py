from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import groups, memberships
from app.extension import get_db
from sqlalchemy import select
from app.services.group_code import generate_group_code
from app.services.jwt_service import get_current_user

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

@router.delete('/groups/{group_id}/members/{member_id}')
async def remove_member(
    group_id: str,
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):

    group = (
        await db.execute(
            select(groups.Group).where(
                groups.Group.id == group_id
            ))
    ).scalar_one_or_none()

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can remove members")

    membership = (
        await db.execute(
            select(memberships.Membership).where(
                memberships.Membership.user_id == member_id,
                memberships.Membership.group_id == group_id
            ))
    ).scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    await db.delete(membership)
    await db.commit()

    return JSONResponse(content={"ok": 200},status_code=200)