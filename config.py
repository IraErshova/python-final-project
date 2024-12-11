import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
BOT_API = os.getenv("BOT_API")
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
