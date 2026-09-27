import chromadb
from app.models.chunk import Chunk
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="papers")
def add_chunks(chunks,vectors):
    collection.add(
        ids=[str(chunk.chunk_id) for chunk in chunks],
        documents= [chunk.text for chunk in chunks],
        embeddings=vectors.tolist(),
        #[{}]列表里面装字典
        #[]:一堆东西。{}:一段东西里面的详细属性
        metadatas=[
            {
                "chunk_id": chunk.chunk_id,
                #",".join(map(str，xxx)):把一个列表转换成一个字符串,并将原列表的字符串元素用,隔开
                "pages": ",".join(map(str,chunk.pages))
            }
        for chunk in chunks
        ]
    )