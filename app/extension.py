from sqlalchemy.orm import declarative_base
from fastapi.templating import Jinja2Templates
from pathlib import Path

Base = declarative_base()

BASE_DIREC = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIREC/'templates')