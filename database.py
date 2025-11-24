from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

URL_DATABASE = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()
