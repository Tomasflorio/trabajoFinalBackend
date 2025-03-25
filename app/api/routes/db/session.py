from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://"+os.getenv("DB_USER")+":"+os.getenv("DB_USER_PASS")+"@"+os.getenv("DB_SERVER")+"/"+os.getenv("DATABASE_NAME"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
