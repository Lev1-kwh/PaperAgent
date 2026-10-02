from app.models import chunk
from app.services.embedding_service import embed_text
from app.services.llm_service import ask_llm
from app.services.vector_service import search_chunks


def ask_paper(question):
    query_vector = embed_text(question)
    chunks = search_chunks(query_vector)
    context = build_context(chunks)
    prompt = build_prompt(context,question)
    answer = ask_llm(prompt)
    sources = [
        {"chunk_id":chunk.chunk_id,
         "pages":chunk.pages,
         "distance":chunk.distance}
        for chunk in chunks
    ]
    return {
        "answer":answer,
        "sources":sources
    }
def build_context(chunks):
    context_parts=[]
    for chunk in chunks:
        pages = "，".join(map(str,chunk.pages))
        context_parts.append(
            #f为f-string（格式化字符串），
            # 往字符串里塞变量
            # 将{chunk['page']}作为字符串打印出来
            f"[第{pages}页]\n{chunk.text}"
        )
    return "\n\n".join(context_parts)
def build_prompt(context,question):
    #三对双引号括起来表示多行字符串
    prompt = f"""
你是一名论文分析助手。

请严格根据提供的论文内容回答问题。

如果论文内容没有相关信息，请明确说明无法从论文片段中找到答案。

不要使用外部知识补充。

    论文内容：
    {context}
    问题：
    {question}
    """
    return prompt