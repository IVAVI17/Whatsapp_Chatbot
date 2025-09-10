import os
import json
from dotenv import load_dotenv

load_dotenv()

raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

try:
    GOOGLE_CREDENTIALS = json.loads(raw_creds)

    if "private_key" in GOOGLE_CREDENTIALS:
        key = GOOGLE_CREDENTIALS["private_key"]

        # Replace escaped \n with actual newlines
        key = key.replace("\\n", "\n").strip()

        GOOGLE_CREDENTIALS["private_key"] = key

except Exception as e:
    print("❌ Error loading GOOGLE_CREDENTIALS:", e)
    GOOGLE_CREDENTIALS = {}