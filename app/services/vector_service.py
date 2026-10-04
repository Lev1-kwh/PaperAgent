import chromadb
from app.models.chunk import Chunk

#新建一个客户端通过客户端操作向量数据库，Persistent代表数据库中的数据会存放到硬盘中
client = chromadb.PersistentClient(path="./chroma_db")
#打开已有表或创建新表，表名为papers
collection = client.get_or_create_collection(name="papers")
#给表加字段以及数据
def add_chunks(chunks,vectors):
    collection.add(
        #id字段：存放id列表，字符串类型
        ids=["_".join([str(chunk.paper_id),str(chunk.chunk_id)]) for chunk in chunks],
        #document：存放chunks的文本内容列表
        documents= [chunk.text for chunk in chunks],
        #embedding：存放切分好的向量列表
        embeddings=vectors.tolist(),
        #[{}]列表里面装字典
        #[]:一堆东西。{}:一段东西里面的详细属性
        #metadatas：存放数据的其他附带信息如chunk的id以及所属的页码
        metadatas=[
            {
                "paper_id":chunk.paper_id,
                "chunk_id": chunk.chunk_id,
                #",".join(map(str，xxx)):把一个列表转换成一个字符串,并将原列表的字符串元素用,隔开
                "pages": ",".join(map(str,chunk.pages))
            }
        for chunk in chunks
        ]
    )
def search_chunks(query_vector,paper_id,top_k=3):
    results = collection.query(
        query_embeddings= [query_vector.tolist()],
        n_results= top_k,
        where={
            'paper_id':paper_id
        }
        )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    chunks=[]
    for i in range(len(documents)):
        chunks.append(
            Chunk(
                paper_id=metadatas[i]["paper_id"],
                chunk_id=metadatas[i]["chunk_id"],
                pages = [int(page) for page in metadatas[i]["pages"].split(",")],
                text=documents[i],
                distance=distances[i]
            )
        )
    return chunks