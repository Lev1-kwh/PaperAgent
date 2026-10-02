from app.services.rag_service import ask_paper
question = "DNA Fountain 是什么？"
answer = ask_paper(question)
print(answer)