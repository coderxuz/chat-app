from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from dotenv import load_dotenv

from os import getenv

load_dotenv()

DB_URL = getenv('DATABASE_URL')
if DB_URL:
    engine = create_engine(DB_URL)
else:
    raise ValueError("DB_URL didn't find")

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
