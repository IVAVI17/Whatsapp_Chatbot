import os
import json
from dotenv import load_dotenv

load_dotenv()

raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

try:
    # Parse the GOOGLE_CREDENTIALS environment variable
    GOOGLE_CREDENTIALS = json.loads(raw_creds)

    # Ensure the private_key is properly formatted
    if "private_key" in GOOGLE_CREDENTIALS:
        key = GOOGLE_CREDENTIALS["private_key"]

        # Replace escaped \\n with actual newlines
        GOOGLE_CREDENTIALS["private_key"] = key.replace("\\n", "\n").strip()

except Exception as e:
    print("❌ Error loading GOOGLE_CREDENTIALS:", e)
    GOOGLE_CREDENTIALS = {}