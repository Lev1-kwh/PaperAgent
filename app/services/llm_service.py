import  os
from dotenv import load_dotenv
from openai import OpenAI
#加载.env中的配置到当前环境变量中
load_dotenv()
#新建客户端用来与DeepSeek API通信
client = OpenAI(
    #从环境变量中取出DEEPSEEK_API_KEY
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
def ask_llm(prompt):
    response = client.chat.completions.create(
        model= "deepseek-flash",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content
