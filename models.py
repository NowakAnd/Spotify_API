from dataclasses import dataclass

@dataclass
class AuthSpotify:
    """Dataclass for Spotify authentication."""
    cli_id: str
    secret_id: str
    redirect_uri: str
    scope: list[str]

@dataclass
class CurrentSongInfo:
    """Dataclass for current song information."""
    progress_ms: int
    artists: list[str]
    song_name: str
    song_id: str
    play_status: bool

@dataclass
class SpotifyTokens:
    """Data class to hold Spotify API tokens."""
    access_token: str
    refresh_token: str
