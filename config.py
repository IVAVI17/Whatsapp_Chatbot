import os
import json
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment variable
GOOGLE_CREDENTIALS = json.loads(os.getenv('GOOGLE_CREDENTIALS', '{}'))