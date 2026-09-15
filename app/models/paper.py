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