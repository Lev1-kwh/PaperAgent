from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
def embed_text(text):
    #encode()支持批量处理所以传递的参数是一个文本列表
    return model.encode(text)
def embed_chunks(chunks):
    texts = [chunk.text for chunk in chunks]
    vectors = model.encode(texts)
    return vectors