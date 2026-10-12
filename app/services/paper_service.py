
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
def get_paper_by_id(paper_id):
    session = SessionLocal()
    try:
        statement = select(Paper).where(
            Paper.paper_id == paper_id
        )
        result = session.execute(statement)
        #.one_or_none:结果必须有且只有一条或者为空
        paper = result.scalars().one_or_none()
        return paper
    finally:
        session.close()
