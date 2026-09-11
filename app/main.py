from fastapi import FastAPI
from app.models import PaperCreate
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "PaperAgent is running"}
@app.post("/papers")
def create_paper(paper:PaperCreate):
    response={}
    response["message"]="paper created"
    response["title"]=paper.title
    response["author"]=paper.author
    return response