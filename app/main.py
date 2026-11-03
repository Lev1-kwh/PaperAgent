from fastapi import FastAPI
from app.routers.paper import router
#创建FastAPI应用实例
app = FastAPI()
print("PaperAgent Started")
#注册论文相关路由
app.include_router(router)
#定义根路径接口
@app.get("/")
def read_root():
    return {"message": "PaperAgent is running"}