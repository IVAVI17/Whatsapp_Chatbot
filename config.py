import os, json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS", "{}"))
