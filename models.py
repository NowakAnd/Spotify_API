from dataclasses import dataclass
from typing import List, TypedDict, List, Optional, Dict, Any

@dataclass
class AuthSpotify:
    """Dataclass for Spotify authentication."""
    cli_id: str
    secret_id: str
    redirect_uri: str
    scope: List[str]

class CurrentSongInfo(TypedDict):
    """Type hint for current song information."""
    progress_ms: int
    artists: List[str]
    song: str
    song_id: str
    play_status: bool

@dataclass
class SpotifyTokens:
    """Data class to hold Spotify API tokens."""
    access_token: str
    refresh_token: str
