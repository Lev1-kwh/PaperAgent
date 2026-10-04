from pydantic import BaseModel
class PaperCreate(BaseModel):
    title: str
    author: str
class PaperResponse(BaseModel):
    paper_id:str
    message: str
    title: str
    author: str
class PaperUploadResponse(BaseModel):
    paper_id: str
    message: str
    filename: str
    text_length: int
    chunk_count: int
class Question(BaseModel):
    paper_id: str
    question: str
class PaperSource(BaseModel):
    paper_id: str
    chunk_id : int
    pages : list[int]
    distance : float
class PaperAskResponse(BaseModel):
 answer: str
 sources: list[PaperSource]
