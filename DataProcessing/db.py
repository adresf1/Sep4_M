from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or DATABASE_URL = 'postgresql://dummy_url'

if DATABASE_URL == 'postgresql://dummy_url':
    print("Application have defaulted to dummy connection string")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)