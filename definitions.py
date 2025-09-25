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
CURRENTLY_PLAYING_ENDPOINT = 'https://api.spotify.com/v1/me/player/currently-playing'

#PATHS
SONGS_CSV_PATH = 'Data/songs.csv'

# Application settings
SONG_ACCEPTANCE_TIME_MS = 40_000  # Time in ms after which a song is considered "played"
DEFAULT_REQUEST_TIMEOUT_SEC = 5    # Default timeout for API requests

# Tracker settings
LOOP_DELAY_SECONDS = 5             # Delay between checks for song changes
MAX_RETRIES = 3                    # Maximum number of retry attempts for API calls
RETRY_DELAY_SECONDS = 2            # Delay between retry attempts