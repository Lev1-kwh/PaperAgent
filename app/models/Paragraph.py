from pydantic import BaseModel


class Paragraph(BaseModel):
    text : str
    pages : list[int]
