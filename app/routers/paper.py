from app.models.paper import PaperResponse,PaperCreate,PaperUploadResponse
from fastapi import APIRouter,UploadFile,File,HTTPException
import os,uuid,pymupdf
from app.services.text_service import  clean_text,split_paragraphs
from app.services.chunk_service import chunk_paragraphs
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
async def  uploads_paper(file:UploadFile = File(...)):
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
    chunks = chunk_paragraphs(paragraphs,1000)
    response = PaperUploadResponse(message="上传成功",
                                   filename=filename,
                                   text_length=text_length,
                                   chunk_count=len(chunks))
    for paragraph in paragraphs:
        print(paragraph)
        print("//////////////////////////")
    for chunk in chunks:
        print(chunk.chunk_id,len(chunk.text))
    return response
