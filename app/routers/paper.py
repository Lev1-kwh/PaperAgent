import logging

from sqlalchemy.orm import session

from app.models.paper import (
    PaperResponse,
    PaperUploadResponse,
    PaperAskResponse,
    Question, PaperDeleteResponse,
)
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os,uuid,pymupdf
from app.services.text_service import  clean_text,split_paragraphs
from app.services.chunk_service import chunk_paragraphs
from app.services.embedding_service import embed_chunks
from app.services.vector_service import add_chunks,delete_chunks
from app.services.rag_service import  ask_paper
from app.database.database import SessionLocal
from sqlalchemy import select
from typing import List
from app.services.paper_service import(
get_paper_by_id,get_all_papers,delete_paper
)
from app.database.paper import Paper

router = APIRouter(prefix="/papers")
'''第 1 步 __file__：Python 给每个 .py 文件自带的模块级变量，
值是这个文件自己的路径。
它不是你定义的——解释器加载模块时自动塞进去的。
关键是它的参照物：文件自身物理位置，
和你在哪个目录敲命令无关。

第 2 步 os.path.abspath(__file__)：转成绝对路径。
这是个防御性包装——历史原因，
被直接执行的脚本（python xxx.py 那个入口文件）的 __file__ 可能是相对路径（取决于你怎么敲的命令），
被 import 的模块则一定是绝对的。
包一层 abspath，两种情况都稳，成本为零。
第 3 步 三层 dirname：每层砍掉路径最后一节：
数层数的方法就是从文件位置往上走，
走到你想要的那级为止。database.py 只要到 app 所以是 2 次，三个 service/router 文件要到项目根所以是 3 次——这就是为什么大家次数不一样。

第 4 步 os.path.join(BASE_DIR, 'chroma_db')：拼接。
Windows 上写 BASE_DIR + '\chroma_db' 碰巧也能跑，
但 join 换到 Linux/Mac（\ 换 /）也不出错
'''
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 获取当前模块对应的日志记录器，
# 用于记录程序运行过程中的信息和异常

logger = logging.getLogger(__name__)

@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    status_code=201
)
async def uploads_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...)
):
    content = await file.read()
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="只允许上传pdf文件"
        )

    unique_filename = str(uuid.uuid4()) + extension
    # BASE_DIR 在模块顶部用 __file__ 锚定项目根目录，
    # uploads 目录固定落在项目根下，不受启动目录（CWD）影响
    upload_dir = os.path.join(BASE_DIR, "uploads")
    # 如果 uploads 目录不存在，就自动创建
    # exist_ok=True 表示目录已经存在时不报错
    os.makedirs(upload_dir, exist_ok=True)
    # 拼接上传目录和文件名，得到完整的文件路径
    path = os.path.join(upload_dir, unique_filename)

    paper_id = str(uuid.uuid4())


    with open(path, "wb") as f:
        f.write(content)
    session = None


    try:
        session = SessionLocal()
        # 使用 with 语句块管理 pdf 文档的生命周期
        with pymupdf.open(path) as pdf:
            total_text_length = 0
            paragraphs = []

            for page_number, page in enumerate(pdf, start=1):
                cleaned_page_text = clean_text(page.get_text())
                total_text_length += len(cleaned_page_text)
                paragraphs.extend(
                    split_paragraphs(cleaned_page_text, page_number)
                )

                # pages[a][0] 中示例：pages 列表中第 a+1 个元素，
                # 也就是第 a+1 个元组，表示这个元组中的第一个元素，对应上面就是页码。
                # 若为 [a][1]，表示第 a+1 个元组中的第二个元素，也就是文本内容。

        text_length = total_text_length

        chunks = chunk_paragraphs(paragraphs, 1000, paper_id)
        vectors = embed_chunks(chunks)
        add_chunks(chunks, vectors)

        paper_record = Paper(
            paper_id=paper_id,
            title=title,
            author=author,
            filename=filename
        )

        try:
            session.add(paper_record)
            session.commit()
        except Exception:
            try:
                session.rollback()
            except Exception:
                logger.exception(
                    "Fail to rollback paper %s", paper_id
                )

            raise

    except Exception:
        try:
            delete_chunks(paper_id)
        except Exception:
            logger.exception(
                "Failed to compensate Chroma chunks for paper_id = %s",
            )
        try:
            os.remove(path)
        except Exception:
            logger.exception(
                "Failed to delete paper %s", paper_id
            )
        raise

    finally:
        if session is not None:
            session.close()


    response = PaperUploadResponse(
        message="上传成功",
        paper_id=paper_id,
        filename=filename,
        title=title,
        author=author,
        text_length=text_length,
        chunk_count=len(chunks)
    )

    return response
@router.post(
    "/ask",
    response_model=PaperAskResponse,
    status_code=200
)
def ask_paper_endpoint(question:Question):
    if not question.question.strip():
        raise HTTPException(status_code=400,
                            detail="问题不能为空")
    session = SessionLocal()
    try:
        statement = select(Paper).where(
        Paper.paper_id ==question.paper_id )
        #执行查询并获取模型对象结果，
        # .first():获取第一条匹配记录，没有匹配项时返回None
        paper_record = session.scalars(statement).first()
        #大致等价于
        ''' SELECT *
            FROM papers
            WHERE paper_id = ?;'''
        if paper_record is None:
            raise HTTPException(status_code=404,
                                detail="论文不存在")
    finally:
        session.close()
    try:
        result = ask_paper(question.paper_id,question.question)
    except Exception as e:
        raise HTTPException(status_code=500,
                                        detail=f"论文问答失败{str(e)}")
    response = PaperAskResponse(answer=result["answer"],
                                sources = result["sources"])
    return response
@router.get(
    "",
    response_model=List[PaperResponse],
    status_code=200
)
def list_papers():
    papers = get_all_papers()
    return papers


@router.get(
    "/{paper_id}",
    response_model=PaperResponse,
    status_code=200
)
def show_paper(paper_id: str):
    paper = get_paper_by_id(paper_id)
    if paper is None:
        raise HTTPException(
            status_code=404,
        detail="Paper not found")
    return paper
@router.delete(
    "/{paper_id}",
    response_model=PaperDeleteResponse,
status_code=200
)
def delete_paper_endpoint(paper_id: str):
    try:
        result = delete_paper(paper_id)
        if result is False:
            raise HTTPException(
            status_code=404,
            detail="Paper not found"
             )
    except HTTPException:
        raise
    except Exception :
        raise HTTPException(
            status_code=500,
             detail="Delete failed")

    return PaperDeleteResponse(
        paper_id=paper_id,
        message="Paper deleted"
    )


