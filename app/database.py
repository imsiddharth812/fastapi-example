from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Keeping below code for reference in case I want to use & run raw SQL using "psycopg2" postgres library directly without using SQLAlchemy
# while True:
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="r00tr00t",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = conn.cursor()
#         print("Database connection was successsful.")
#         break
#     except Exception as error:
#         print("connection to database failed")
#         print("Error :", error)
#         time.sleep(2)
