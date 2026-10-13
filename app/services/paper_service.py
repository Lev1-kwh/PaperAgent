from sqlalchemy import select
from app.database.database import SessionLocal
from app.database.paper import Paper
import chromadb


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
def delete_paper(paper_id):
    session = SessionLocal()
    client = chromadb.PersistentClient(
        path="./chroma_db"
    )
    collection = client.get_collection(name="papers")
    try:
        statement = select(Paper).where(
            Paper.paper_id == paper_id
        )
        paper =  session.scalars(statement).one_or_none()
        if paper is None:
            return False
        collection.delete(where={
            #ChromaDB 的 where 查询针对的就是 metadata，
            # 不是 document，
            # 也不是 embedding。
            # metadata中的paper_id字段进行查找
            "paper_id": paper_id
        })
        session.delete(paper)
        session.commit()
        return True
    except Exception :
        session.rollback()
        raise
    finally:
        session.close()
