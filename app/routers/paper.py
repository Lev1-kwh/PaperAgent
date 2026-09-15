from app.models.paper import PaperResponse,PaperCreate
from fastapi import APIRouter,UploadFile,File,HTTPException
import os,uuid
router = APIRouter(prefix="/papers")
@router.post("",
             response_model=PaperResponse,
             status_code=201)
def create_paper(paper:PaperCreate):
   response = PaperResponse(message="paper created",
                            title=paper.title,
                            author=paper.author)
   return response
@router.post("/upload")
async def  uploads_paper(file:UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()
    if extension!= ".pdf":
        raise HTTPException(status_code=400,
                            detail="只允许上传pdf文件")
    unique_filename = str(uuid.uuid4()) + extension
    with open(os.path.join("uploads",unique_filename),"wb") as f: f.write(content)
    message = "保存成功"
    return message

