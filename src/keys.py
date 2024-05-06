import os
from dotenv import load_dotenv

load_dotenv()
CHATGPT = os.getenv("CHATGPT_KEY")
DALLE = os.getenv("DALLE_KEY")
BING = os.getenv("BING_SESSION")