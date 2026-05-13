from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers.auth import router as auth_router
from app.routers.groups import router as group_router
from app.routers.invite import router as invite_router

load_dotenv()

def create_app():

    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(group_router)
    app.include_router(invite_router)

    return app