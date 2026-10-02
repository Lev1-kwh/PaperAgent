from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: int
    text: str
    pages : list[int]
    distance : float | None = None

