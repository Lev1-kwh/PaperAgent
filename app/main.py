from fastapi import FastAPI
from app.models.paper import PaperResponse, PaperCreate
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "PaperAgent is running"}
@app.post("/papers", response_model=PaperResponse,
          status_code=201)
def create_paper(paper:PaperCreate):
   response = PaperResponse(message="paper created",
                            title=paper.title,
                            author=paper.author)
   return response
