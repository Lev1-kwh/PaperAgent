from app.models.paper import PaperResponse,PaperCreate,PaperUploadResponse
from fastapi import APIRouter,UploadFile,File,HTTPException
import os,uuid,pymupdf
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
    text = ""
    for page in pdf:
        text+=page.get_text()
    response = PaperUploadResponse(message="上传成功",
                                   filename=filename,
                                   text_length=len(text),)
    return response
