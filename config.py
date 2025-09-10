# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()

# raw_creds = os.getenv("GOOGLE_CREDENTIALS", "{}")

# try:
#     GOOGLE_CREDENTIALS = json.loads(raw_creds)

#     if "private_key" in GOOGLE_CREDENTIALS:
#         key = GOOGLE_CREDENTIALS["private_key"]

#         # Convert escaped newlines into real ones
#         key = key.replace("\\n", "\n").strip()

#         # Normalize BEGIN/END lines
#         if not key.startswith("-----BEGIN PRIVATE KEY-----"):
#             key = "-----BEGIN PRIVATE KEY-----\n" + key
#         if not key.endswith("-----END PRIVATE KEY-----"):
#             key = key + "\n-----END PRIVATE KEY-----"

#         # Ensure no spaces at line ends
#         key = "\n".join(line.strip() for line in key.splitlines())

#         GOOGLE_CREDENTIALS["private_key"] = key

# except Exception as e:
#     print("❌ Error loading GOOGLE_CREDENTIALS:", e)
#     GOOGLE_CREDENTIALS = {}

import os
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
