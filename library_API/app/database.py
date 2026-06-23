from sqlmodel import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

MARIADB_DATABASE_URL = os.environ.get("DATABASE_URL")
if not MARIADB_DATABASE_URL:
    raise RuntimeError(
        "Environment variable DATABASE_URL is not set. "
        "Set it in docker-compose.yaml, e.g. "
        "mysql+pymysql://<user>:<password>@<db-host>:3306/<database>"
    )
engine = create_engine(MARIADB_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
