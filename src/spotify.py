from typing import Any, Dict, Optional

from definitions import *
from logger import logger
from models import AuthSpotify, CurrentSongInfo
from spotify_api import SpotifyAPI


class Spotify:
    """A client for interacting with the Spotify Web API.
    
    This class provides methods to authenticate with the Spotify API and fetch
    various types of music data including artist information, tracks, and user's
    listening history.
    """
    def __init__(self, auth_spotify: AuthSpotify, user: bool = False) -> None:
        """Initialize the Spotify client with empty tokens."""
        self.spotify_api = SpotifyAPI(auth_spotify, user)

    def search_artist(self, artist_name: str) -> Dict[str, Any]:
        """Search for an artist by name.
        
        Args:
            artist_name: Name of the artist to search for
            
        Returns:
            Dict containing artist information
        """
        artists = (self.spotify_api.search(search_query=artist_name, search_type="artist", limit=1)
                   .get("artists", {}).get("items", []))
        if not artists:
            raise ValueError(f"No artist found with name: {artist_name}")
            
        logger.info(f"Artist '{artist_name}' found.")
        return artists[0]

    def get_information_current_song(self) -> Optional[CurrentSongInfo]:
        """Get information about the currently playing song.

        If no song is currently playing, or if a podcast is currently playing instead
        of a song, this method returns None.

        Returns:
            Optional[CurrentSongInfo]: Information about the currently playing song, or None
            if no song is currently playing.
        """
        response = self.spotify_api.get_currently_playing()

        if response is None:
            logger.info("No song is currently playing.")
            return None

        if response.get("currently_playing_type") == "episode":
            logger.info("Podcast is currently playing instead of a song.")
            return None

        song_info = CurrentSongInfo(
            progress_ms = response["progress_ms"],
            artists = [artist["name"] for artist in response["item"]["album"]["artists"]],
            song_name= response["item"]["name"],
            song_id= response["item"]["id"],
            play_status = response["is_playing"]
        )

        logger.info(f"Retrieved information for current song: {song_info.song_name}, {song_info.artists}, "
                    f"{song_info.progress_ms}")
        return song_info

    def get_last_listened(
        self, 
        after_unix_timestamp: int, 
        limit: int = 50
        ) -> Dict[str, Any]:
        """Get recently played tracks for the current user.
        
        Args:
            after_unix_timestamp: Unix timestamp in milliseconds. Only return tracks 
                                played after this timestamp.
            limit: Maximum number of items to return (1-50).
            
        Returns:
            Dict containing recently played tracks
            
        Raises:
            ValueError: If limit is not between 1 and 50
            HTTPError: If the API request fails
        """
        if not 1 <= limit <= 50:
            raise ValueError("Limit must be between 1 and 50")
            
        url = "https://api.spotify.com/v1/me/player/recently-played"
        headers = self._get_auth_header()
        params = {
            "limit": limit,
            "after": after_unix_timestamp
        }
        
        response = get(url, headers=headers, params=params)
        response.raise_for_status()
        
        logger.info(
            f"Retrieved {limit} recently played tracks after "
            f"{after_unix_timestamp}"
        )
        return response.json()


def main() -> None:
    """Example usage of the Spotify client."""
    scopes = [
        "playlist-read-private",
        "user-read-currently-playing",
        "user-read-recently-played"
    ]
    spotify = Spotify(auth_spotify=AuthSpotify(cli_id=CLI_ID,
                                               secret_id=SECRET_ID,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scopes),
                      user=True)

    current_song = spotify.get_information_current_song()
            
    pass


if __name__ == "__main__":
    main()
