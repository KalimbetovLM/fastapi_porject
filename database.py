from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://postgres:postgres@localhost:5433/fastapi_project_db",echo=True)

Base = declarative_base()

session = sessionmaker()





