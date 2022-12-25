from sqlmodel import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

MARIADB_DATABASE_URL = "mysql+pymysql://libraryAPI:hallowelt@localhost:3306/library"

engine = create_engine(MARIADB_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
