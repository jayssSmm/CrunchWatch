from sqlalchemy.orm import declarative_base
from fastapi.templating import Jinja2Templates
from pathlib import Path
import redis
import os
from dotenv import loadenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

loadenv()

Base = declarative_base()
redis_url = os.getenv("REDIS_URL")
database_url = os.getenv("DATABASE_URL")

BASE_DIREC = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIREC/'templates')

redis_client = redis.Redis.from_url(
    redis_url,
    decode_responses=True
)

engine = create_async_engine(DATABASE_URL)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session