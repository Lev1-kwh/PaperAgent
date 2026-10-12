from sqlalchemy import select
from app.database.database import SessionLocal
from app.database.paper import Paper
def get_all_papers():
    session = SessionLocal()
    try:
        #数据库执行SQL进行整表查询
        statement = select(Paper)
        #数据库返回results对象（paper，）元组形式
        results = session.execute(statement)
        #scalars()取第一列；all()将第一列paper转换为Paper对象
        papers = results.scalars().all()
        return papers
    finally:
        session.close()