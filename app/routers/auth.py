from fastapi import APIRouter, Request
from app.extension import templates

router = APIRouter()

@router.get('/login')
async def login(requests:Request):
    return templates.TemplateResponse(
        requests,
        "login.html",
        {"request":requests},
    )