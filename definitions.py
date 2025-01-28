from dotenv import load_dotenv
import os

load_dotenv()
CLI_ID = os.getenv("CLIENT_ID")
SECRET_ID = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = 'https://accounts.spotify.com/api/token'
AUTH_URL = 'https://accounts.spotify.com/authorize'
SEARCH_URL = 'https://api.spotify.com/v1/search?'