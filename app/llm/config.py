import os

from dotenv import load_dotenv


load_dotenv()



DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY"
)


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "deepseek"
)
