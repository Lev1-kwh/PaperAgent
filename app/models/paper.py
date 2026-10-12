from datetime import datetime
from pydantic import BaseModel
class PaperCreate(BaseModel):
    title: str
    author: str
class PaperUploadResponse(BaseModel):
    paper_id: str
    message: str
    filename: str
    title: str
    author: str
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
class PaperResponse(BaseModel):
     paper_id: str
     title: str
     author: str
     filename: str
     created_at: datetime
     #Pydantic允许从Paper对象属性读取数据，生成Response Model。
     class Config:
        from_attributes= True

