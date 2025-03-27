from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_USER_PASS = os.getenv("DB_USER_PASS", "password")
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DATABASE_NAME = os.getenv("DATABASE_NAME", "test_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}@{DB_SERVER}:8080/{DATABASE_NAME}"
#print("DATABASE_URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
