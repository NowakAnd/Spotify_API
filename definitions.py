from dotenv import load_dotenv
import os

#ENV
load_dotenv()
CLI_ID = os.getenv("CLIENT_ID")
SECRET_ID = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

#AUTH
TOKEN_URL = 'https://accounts.spotify.com/api/token'
AUTH_URL = 'https://accounts.spotify.com/authorize'

#API ENDPOINTS
SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search?'

#PATHS
SONGS_CSV_PATH = 'Data/songs.csv'

SONG_ACCEPTANCE_TIME_MS = 40_000
DEFAULT_REQUEST_TIMEOUT_SEC = 5