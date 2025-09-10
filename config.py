import os
import json
from dotenv import load_dotenv

load_dotenv()

raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

try:
    GOOGLE_CREDENTIALS = json.loads(raw_creds)

    # Fix private_key formatting (convert \\n → \n safely)
    if "private_key" in GOOGLE_CREDENTIALS:
        key = GOOGLE_CREDENTIALS["private_key"]

        # Replace escaped newlines with real newlines
        key = key.replace("\\n", "\n").strip()

        # Ensure it has proper BEGIN/END lines
        if not key.startswith("-----BEGIN PRIVATE KEY-----"):
            key = "-----BEGIN PRIVATE KEY-----\n" + key
        if not key.endswith("-----END PRIVATE KEY-----"):
            key = key + "\n-----END PRIVATE KEY-----"

        GOOGLE_CREDENTIALS["private_key"] = key
except Exception as e:
    print("Error loading GOOGLE_CREDENTIALS:", e)
    GOOGLE_CREDENTIALS = {}
