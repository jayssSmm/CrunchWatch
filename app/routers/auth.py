from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.extension import templates, redis_client, get_db
from app.schema import RegisterRequest, VerifyOTPRequest, LoginRequest
from fastapi.responses import JSONResponse
from app.models.user import User
from app.services import otp_service, auth_service, mail_services, jwt_service
import json

router = APIRouter()

@router.get('/login')
async def login(requests:Request):
    return templates.TemplateResponse(
        "login.html",
        {"request":requests},
    )

@router.get('/register')
async def register(request:Request):
    return templates.TemplateResponse(
        'register.html',
        {"request":request}, 
    )

@router.post('/register')
async def register_person(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    name = payload.name.lower()
    email = payload.email.strip().lower()

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        return JSONResponse(content={"error": "This email is already registered."}, status_code=409)

    otp = otp_service.generate_otp()
    pending = {
        "name": name,
        "email": email,
        "password_hash": auth_service.hash_password(payload.password),
        "otp": otp,
    }
    redis_client.setex(f"otp:{email}", otp_service.OTP_TTL, json.dumps(pending))

    mail_services.send_otp(
        receiver_email=email,
        receiver_name=name,
        expire_time=otp_service.OTP_TTL // 60,
        otp_code=otp
    )

    return JSONResponse(content={"ok": True}, status_code=200)

@router.post('/verify-otp')
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    email = payload.email
    entered_otp = payload.otp

    raw = redis_client.get(f"otp:{email}")
    if not raw:
        return JSONResponse(content={"error": "OTP expired. Please register again."}, status_code=410)

    pending = json.loads(raw)

    if str(entered_otp) != str(pending.get('otp')):
        return JSONResponse(content={"error": "Invalid OTP. Please try again."}, status_code=400)

    new_user = User(
        name=pending['name'],           # matches what you stored
        email=pending['email'],
        password_hash=pending['password_hash']
    )
    db.add(new_user)
    await db.commit()

    token = jwt_service.create_access_token(data={'sub':str(new_user.id)})
    response = JSONResponse(content={"ok": True}, status_code=200)

    response.set_cookie(
        key='access_token',
        value=token,
        max_age=3600,
        expires=3600,
        httponly=True,
        path='/',
        secure=True,
    )

    redis_client.delete(f"otp:{email}")
    return response

@router.post('/login')
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    email = payload.email
    password = payload.password

    if not email or not password:
        return JSONResponse(content={'error':'Email and password are required.'}, status_code=400)
    
    user = await db.execute(select(User).where(User.email == email))
    if not user.scalar_one_or_none(): 
        return JSONResponse(content={'error':'"Wrong credentials. Try again.'}, status_code=401)
    
    result = auth_service.verify_password(password, user.password_hash)

    if not result:
        return JSONResponse(content={'error':'"Wrong credentials. Try again.'}, status_code=401)
    
    token = jwt_service.create_access_token(data={'sub':str(user.id)})
    response = JSONResponse(content={'ok':True},status_code=200)

    response.set_cookie(
        key='access_token',
        path='/',
        httponly=True,
        secure=True,
        max_age=3600,
        expires=3600,
        value=token,
    )

    return response