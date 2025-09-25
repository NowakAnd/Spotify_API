import base64
from http import HTTPStatus
from typing import Any

import requests

from requests import HTTPError

from auth_server import AuthServer
from definitions import TOKEN_URL, DEFAULT_REQUEST_TIMEOUT_SEC, SEARCH_ENDPOINT, CURRENTLY_PLAYING_ENDPOINT
from logger import logger
from models import AuthSpotify, SpotifyTokens


class SpotifyAPI:
    def __init__(self, auth_spotify: AuthSpotify, user: bool = False) -> None:
        self.auth_spotify = auth_spotify
        self.access_tokens: SpotifyTokens = self._get_token() if not user else self._get_user_token()

    def __create_auth_base64(self) -> str:
        """Create base64 encoded authorization string.

        Returns:
            str: Base64 encoded client credentials
        """
        auth_string = f"{self.auth_spotify.cli_id}:{self.auth_spotify.secret_id}"
        auth_bytes = auth_string.encode("utf-8")
        return base64.b64encode(auth_bytes).decode("utf-8")

    def _get_token(self, timeout: int = DEFAULT_REQUEST_TIMEOUT_SEC) -> SpotifyTokens:
        """Get an access token using client credentials flow.

        Returns:
            SpotifyTokens: Object containing access token

        Raises:
            HTTPError: If the token request fails
        """
        headers = {
            "Authorization": f"Basic {self.__create_auth_base64()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form = {"grant_type": "client_credentials"}

        try:
            response = requests.post(url=TOKEN_URL,
                                     headers=headers,
                                     data=form,
                                     timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise HTTPError(f"Failed to get token: {e}") from e

        logger.info("Client Credentials access token retrieved.")
        return SpotifyTokens(
            access_token=response.json()["access_token"],
            refresh_token=response.json().get("refresh_token", "")
        )

    def _get_user_token(self, timeout: int = DEFAULT_REQUEST_TIMEOUT_SEC) -> SpotifyTokens:
        """Get user access token using authorization code flow.

        Returns:
            SpotifyTokens: Object containing access and refresh tokens

        Raises:
            HTTPError: If the token request fails
        """
        headers = {
            "Authorization": f"Basic {self.__create_auth_base64()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        server = AuthServer(scope=" ".join(self.auth_spotify.scope))

        form = {
            "grant_type": "authorization_code",
            "code": server.callback(),
            "redirect_uri": self.auth_spotify.redirect_uri,
        }

        response = requests.post(url=TOKEN_URL,
                                 headers=headers,
                                 data=form,
                                 timeout=timeout)
        logger.info("User access token retrieved.")
        return SpotifyTokens(
            access_token=response.json()["access_token"],
            refresh_token=response.json().get("refresh_token", "")
        )

    def _get_auth_header(self) -> dict[str, str]:
        """Get authorization header with current access token.

        Returns:
            Dict[str, str]: Authorization header
        """
        return {"Authorization": f"Bearer {self.access_tokens.access_token}"}

    def search(self, search_query: str,
               search_type: str,
               market: str = "",
               limit: int = 10,
               offset: int = 0,
               include_external: str = "",
               timeout: int = DEFAULT_REQUEST_TIMEOUT_SEC) -> dict[str, Any]:
        """
        Search for an item of a certain type.
        https://developer.spotify.com/documentation/web-api/reference/search

        Args:
            search_query: Query string to search for.
            search_type: Type of item to search for (e.g. artist, track, album).
            market: An ISO 3166-1 alpha-2 country code or the string from_token.
            limit: The maximum number of items to return (0-50).
            offset: The index of the first item to return.
            include_external: If set to "artist", the response will include any artists that are associated with the item that is returned.
            timeout: The maximum number of seconds to wait for the request to complete.

        Returns:
            Dict[str, Any]: The server response.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        params = {
            "q": search_query,
            "type": search_type,
            "market": market,
            "limit": limit,
            "offset": offset,
            "include_external": include_external
        }

        response = requests.get(url=SEARCH_ENDPOINT,
                                headers=self._get_auth_header(),
                                params=params,
                                timeout=timeout)

        response.raise_for_status()

        return response.json()

    def get_currently_playing(self, timeout: int = DEFAULT_REQUEST_TIMEOUT_SEC) -> dict[str, Any] | None:
        """
        Get information about the user's currently playing track.
        https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track

        Required scope:
            user-read-currently-playing

        Args:
            timeout: The maximum number of seconds to wait for the request to complete.

        Returns:
            Dict[str, Any]: The server response.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        response = requests.get(url=CURRENTLY_PLAYING_ENDPOINT,
                                headers=self._get_auth_header(),
                                timeout=timeout)
        if HTTPStatus.NO_CONTENT == response.status_code:
            return None
        response.raise_for_status()
        return response.json()