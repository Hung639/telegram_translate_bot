# config.py

import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Danh sách admin cách nhau bằng dấu phẩy, ví dụ: "123456789,987654321"
raw_admins = os.getenv("AUTHORIZED_USERS", "")
AUTHORIZED_USERS = [int(uid.strip()) for uid in raw_admins.split(",") if uid.strip().isdigit()]
