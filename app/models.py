from pydantic import BaseModel
class PaperCreate(BaseModel):
    title: str
    author: str

