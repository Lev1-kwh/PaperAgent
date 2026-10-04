from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: int
    paper_id: str
    text: str
    pages : list[int]
    distance : float | None = None

