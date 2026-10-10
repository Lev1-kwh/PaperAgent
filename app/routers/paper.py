from app.models.paper import PaperResponse,PaperCreate,PaperUploadResponse
from app.models.paper import PaperSource,PaperAskResponse,Question
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os,uuid,pymupdf
from app.services.text_service import  clean_text,split_paragraphs
from app.services.chunk_service import chunk_paragraphs
from app.services.embedding_service import embed_chunks
from app.services.vector_service import add_chunks
from app.services.rag_service import  ask_paper
from app.database.database import SessionLocal
from app.database.paper import Paper
from sqlalchemy import select
router = APIRouter(prefix="/papers")
@router.post("",
             response_model=PaperResponse,
             status_code=201)
def create_paper(paper:PaperCreate):
   response = PaperResponse(message="paper created",
                            title=paper.title,
                            author=paper.author)
   return response
@router.post(
    "/upload",
             response_model=PaperUploadResponse,
             status_code=201)
async def  uploads_paper(file:UploadFile = File(...),
                         title:str=Form(...),
                         author:str=Form(...),):
    content = await file.read()
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()
    if extension!= ".pdf":
        raise HTTPException(status_code=400,
                            detail="只允许上传pdf文件")
    unique_filename = str(uuid.uuid4()) + extension
    path = os.path.join("uploads", unique_filename)
    with open(path,"wb") as f: f.write(content)
    pdf = pymupdf.open(path)
    total_text_length  = 0
    paragraphs=[]
    for page_number, page in enumerate(pdf,start=1):
        cleaned_page_text = clean_text(page.get_text())
        total_text_length += len(cleaned_page_text)
        paragraphs.extend(split_paragraphs(cleaned_page_text, page_number))
        #pages[a][0]中示pages列表中第a+1个元素，
        #也就是第a+1个元组，表示这个元组中的第一个元素，对应上面就是页码。
        #若为[a][1]表示第a+1个元组中的第二个元素，也就是文本内容

    text_length = total_text_length
    paper_id = str(uuid.uuid4())
    chunks = chunk_paragraphs(paragraphs,1000,paper_id)
    vectors = embed_chunks(chunks)
    add_chunks(chunks,vectors)
    session = SessionLocal()
    try:
        paper_record = Paper(
            paper_id = paper_id,
            title = title,
            author = author,
            filename = filename
        )
        session.add(paper_record)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    response = PaperUploadResponse(message="上传成功",
                                   paper_id=paper_id,
                                   filename=filename,
                                   title =title,
                                   author =author,
                                   text_length=text_length,
                                   chunk_count=len(chunks))
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

