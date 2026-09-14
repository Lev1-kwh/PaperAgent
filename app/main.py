from fastapi import FastAPI
from app.routers.paper import router
app = FastAPI()
print("PaperAgent Started")
app.include_router(router)
@app.get("/")
def read_root():
    return {"message": "PaperAgent is running"}