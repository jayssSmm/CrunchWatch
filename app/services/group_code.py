import random
import string
from app.models.groups import Group
from sqlalchemy import select

def generate_group_code() -> str:
    def segment(length: int) -> str:
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    return f"{segment(10)}"

async def update_group(id, name, description, db):
    user = (await db.execute(select(Group).where(Group.id==id))).scalar_one_or_none()
    if name:
        user.name = name
    if description:
        user.description = description

    await db.commit()