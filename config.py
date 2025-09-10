import os
import json
from dotenv import load_dotenv

load_dotenv()

# Load credentials from env
raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

try:
    GOOGLE_CREDENTIALS = json.loads(raw_creds)

    # Fix private_key formatting (convert \\n → \n)
    if "private_key" in GOOGLE_CREDENTIALS:
        GOOGLE_CREDENTIALS["private_key"] = GOOGLE_CREDENTIALS["private_key"].replace("\\n", "\n")
except json.JSONDecodeError:
    GOOGLE_CREDENTIALS = {}
