import os
# os.environ["HTTP_PROXY"] = os.getenv(
#     "HTTP_PROXY"
# )
#
# os.environ["HTTPS_PROXY"] = os.getenv(
#     "HTTPS_PROXY"
# )
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv(            "DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0,
        timeout=30,
        max_retries=1
    )
