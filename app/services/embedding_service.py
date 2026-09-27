from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
def embed_text(text):
    return model.encode(text)
def embed_chunks(chunks):
    texts = [chunk.text for chunk in chunks]
    vectors = model.encode(texts)
    return vectors