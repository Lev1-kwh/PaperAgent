from datetime import datetime,timezone
from sqlalchemy import Column,  String, DateTime
from sqlalchemy.orm import DeclarativeBase

from app.database.database import engine


#类似于java中@Entity
class Base(DeclarativeBase):
    pass
def utc_now():
    return datetime.now(timezone.utc)
#SQLAIchemy通过Base知道目前有哪些数据库模型
class Paper(Base):
    __tablename__ = 'papers'
    paper_id = Column(String, primary_key=True)
    title = Column(String,nullable=False)
    author = Column(String,nullable=False)
    filename = Column(String,nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now,
                       onupdate=utc_now)
#根据Base里面登记的所有SQLALchemy模型，在engine所连接的数据库中创建对应的表
Base.metadata.create_all(engine)

