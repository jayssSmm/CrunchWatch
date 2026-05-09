import random

OTP_TTL = 600 # 10 min

def generate_otp() -> int:
    return random.randint(100000, 999999)