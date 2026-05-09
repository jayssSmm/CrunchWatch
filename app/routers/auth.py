from fastapi import APIRouter, Request
from app.extension import templates, redis_client
from fastapi.responses import JSONResponse
from app.models.user import User
from app.services import otp_service, auth_service, mail_services
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

@router.post('register')
async def register_person(request:Request):
    data =  await request.json()
    name = data.get('name').strip().lower()
    email = data.get('email').strip().lower()
    passwd = data.get('password')

    if not name or not email or not passwd:
        return JSONResponse(content={"error": "Full name, email, and password are required."}, status_code=400)
    
    existing_user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()
    if existing_user:
        return JSONResponse(content={"error": "This email is already registered."}, status_code=409)
    
    otp = otp_service.generate_otp()

    pending = {
        "name": name,
        "email": email,
        "password_hash": auth_service.hash_password(passwd),
        "otp": otp,
    }
    redis_client.setex(f"otp:{email}", otp_service.OTP_TTL, json.dumps(pending))

    mail_services.send_otp(
        receiver_email=email,
        receiver_name=name,
        expire_time= otp_service.OTP_TTL // 60,   # 10 min
        otp_code=otp
    )

    return JSONResponse(content={"ok": True},status_code=200)

@router.post('/verify-otp')
async def verifyOtp(request:Request):
    data = await request.json()
    email =  data.get('email','').strip().lower()
    entered_otp = data.get('otp')

    raw = redis_client.get(f"otp:{email}")
    if not raw:
        return JSONResponse(content={"error": "OTP expired. Please register again."}, status_code=410)
    
    pending = json.loads(raw)

    if str(entered_otp) != str(pending.get('otp')):
        return JSONResponse(content={"error": "Invalid OTP. Please try again."}, status_code=400)
    
    new_user = User(
        full_name=pending['full_name'],
        email=pending['email'],
        password_hash=pending['password_hash']
    )
    db.session.add(new_user)
    db.session.commit()

    redis_client.delete(f"otp:{email}")