from pydantic import BaseModel
class PaperCreate(BaseModel):
    title: str
    author: str
class PaperResponse(BaseModel):
    message: str
    title: str
    author: str
