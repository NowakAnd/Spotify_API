import base64
import json
import webbrowser

from requests import post, get
from http.client import OK

from auth_server import AuthServer
from logger import logger, function_logging
from definitions import TOKEN_URL, CLI_ID, SECRET_ID, REDIRECT_URI


#CREATE .env WHERE YOU ARE GOING TO STORE CLIENT_ID AND SECRET_ID FROM SPOTIFY API

class Spotify:
    def __init__(self) -> None:
        self.token = None
        self.refresh_token = None

    @function_logging
    def get_token(self) -> str:
        auth_string : str = CLI_ID + ":" + SECRET_ID
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = TOKEN_URL
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form = {
            "grant_type": "client_credentials"
        }
        result = post(url, headers=headers, data=form)
        if result.status_code == OK:
            logger.info("Client Credentials access token retrieved.")
            json_result = json.loads(result.content)
            self.token = json_result['access_token']
            return json_result
        else:
            logger.exception(f"Non-success status code: {result.status_code}")
            raise Exception(f"Non-success status code: {result.status_code}")

    @function_logging
    def get_user_token(self, scope: str) -> str:
        auth_string: str = CLI_ID + ":" + SECRET_ID
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = TOKEN_URL
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        server = AuthServer(scope=scope)
        form = {
            "grant_type": "authorization_code",
            'code': server.callback(),
            'redirect_uri': REDIRECT_URI,
        }
        result = post(url, headers=headers, data=form)
        if result.status_code == OK:
            logger.info("Client Credentials access token retrieved.")
            json_result = json.loads(result.content)
            self.token = json_result['access_token']
            self.refresh_token = json_result['refresh_token']
            return json_result
        else:
            logger.exception(f"Non-success status code: {result.status_code}")
            raise Exception(f"Non-success status code: {result.status_code}")

    def _get_auth_header(self) -> dict[str:str]:
        return {"Authorization": "Bearer " + self.token}

    @function_logging
    def search_artist(self, artist_name: str) -> dict:
        url = 'https://api.spotify.com/v1/search?'
        headers = self._get_auth_header()
        query = f"q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        if result.status_code == OK:
            logger.info(f"Artist {artist_name} found.")
            ret = json.loads(result.content)["artists"]["items"]
            return ret[0]
        else:
            logger.exception(f"Exception occurred: {result.status_code}")
            result.raise_for_status()

    @function_logging
    def get_song_by_artist_id(self, artist_id: str):
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
        headers = self._get_auth_header()
        result = get(url, headers=headers)
        if result.status_code == OK:
            logger.info(f"Top songs of {artist_id} found.")
            ret = json.loads(result.content)["tracks"]
            return ret
        else:
            logger.exception(f"Exception occurred: {result.status_code}")
            result.raise_for_status()



if __name__ == "__main__":
    spotify = Spotify()
    spotify.get_user_token('playlist-read-private')
    print(spotify.token)
    print(spotify.refresh_token)

    art_id = spotify.search_artist("Babymetal")["id"]
    songs = spotify.get_song_by_artist_id(art_id)

    for index, song in enumerate(songs):
        print(f"{index+1}: {song['name']}")
