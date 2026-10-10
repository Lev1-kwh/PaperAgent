import sqlalchemy
from sqlalchemy.orm import sessionmaker

database_url = "sqlite:///D:/PaperAgent/app/database.db"
engine = sqlalchemy.create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

