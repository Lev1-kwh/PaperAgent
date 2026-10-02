from pydantic import BaseModel
class PaperCreate(BaseModel):
    title: str
    author: str
class PaperResponse(BaseModel):
    message: str
    title: str
    author: str
class PaperUploadResponse(BaseModel):
    message: str
    filename: str
    text_length: int
    chunk_count: int
class Question(BaseModel):
    question: str
class PaperSource(BaseModel):
    chunk_id : int
    pages : list[int]
    distance : float
class PaperAskResponse(BaseModel):
 answer: str
 sources: list[PaperSource]
