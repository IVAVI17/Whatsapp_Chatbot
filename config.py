import os
import json
from dotenv import load_dotenv

load_dotenv()

raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

try:
    # Parse the GOOGLE_CREDENTIALS environment variable
    GOOGLE_CREDENTIALS = json.loads(raw_creds)
    
    # Logging raw type check
    print("✅ GOOGLE_CREDENTIALS type:", type(GOOGLE_CREDENTIALS))


    # Ensure the private_key is properly formatted
    if "private_key" in GOOGLE_CREDENTIALS:
        key = GOOGLE_CREDENTIALS["private_key"]

        # Replace escaped \\n with actual newlines
        GOOGLE_CREDENTIALS["private_key"] = key.replace("\\n", "\n").strip()
        print("🔑 Private key loaded successfully:")
        print("   Start:", GOOGLE_CREDENTIALS["private_key"][:30], "...")
        print("   End:  ", GOOGLE_CREDENTIALS["private_key"][-30:], "...")


        # Debugging: Log the first few characters of the private key (optional)
        print("Private key loaded successfully:", GOOGLE_CREDENTIALS["private_key"][:30], "...")

except Exception as e:
    print("❌ Error loading GOOGLE_CREDENTIALS:", e)
    GOOGLE_CREDENTIALS = {}
    