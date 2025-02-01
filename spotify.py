import base64
import json
import time

from Tools.scripts.generate_opcode_h import header
from requests import post, get
from http.client import OK

from auth_server import AuthServer
from logger import logger, function_logging
from definitions import TOKEN_URL, CLI_ID, SECRET_ID, REDIRECT_URI, SEARCH_URL


#CREATE .env WHERE YOU ARE GOING TO STORE CLIENT_ID AND SECRET_ID FROM SPOTIFY API

class Spotify:
    def __init__(self) -> None:
        self.token = None
        self.refresh_token = None

    @staticmethod
    def _create_auth_base64() -> str:
        auth_string: str = CLI_ID + ":" + SECRET_ID
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
        return auth_base64

    @function_logging
    def get_token(self) -> str:
        headers = {
            "Authorization": "Basic " + self._create_auth_base64(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form = {
            "grant_type": "client_credentials"
        }
        result = post(TOKEN_URL, headers=headers, data=form)

        if result.status_code == OK:
            logger.info("Client Credentials access token retrieved.")
            json_result = json.loads(result.content)
            self.token = json_result['access_token']
            return json_result
        else:
            logger.exception(f"Non-success status code: {result.status_code}")
            raise Exception(f"Non-success status code: {result.status_code}")

    @function_logging
    def get_user_token(self, scope: str) -> bool:
        headers = {
            "Authorization": "Basic " + self._create_auth_base64(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        server = AuthServer(scope=scope)
        form = {
            "grant_type": "authorization_code",
            'code': server.callback(),
            'redirect_uri': REDIRECT_URI,
        }
        result = post(TOKEN_URL, headers=headers, data=form)

        if result.status_code == OK:
            logger.info("Client Credentials access token retrieved.")
            json_result = json.loads(result.content)
            self.token = json_result['access_token']
            self.refresh_token = json_result['refresh_token']
            return True
        else:
            logger.exception(f"Non-success status code: {result.status_code}")
            raise Exception(f"Non-success status code: {result.status_code}")

    def _get_auth_header(self) -> dict[str:str]:
        return {"Authorization": "Bearer " + self.token}

    @function_logging
    def search_artist(self, artist_name: str) -> dict:
        headers = self._get_auth_header()
        query = f"q={artist_name}&type=artist&limit=1"

        query_url = SEARCH_URL + query
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

    def get_information_current_song(self) -> dict[str: str|bool|int|list[str]]:
        url = 'https://api.spotify.com/v1/me/player/currently-playing'
        headers = self._get_auth_header()
        result = get(url=url, headers=headers)
        if result.status_code == OK:
            logger.info('Information about current song received')
            ret = json.loads(result.content)
            artist_list = []
            for artist in ret['item']['album']['artists']:
                artist_list.append(artist['name'])
            ret_dict = {'progress_ms': ret['progress_ms'],
                        'artists': artist_list,
                        'song': ret['item']['name'],
                        'song_id': ret['item']['id'],
                        'play_status': ret['is_playing']}
            return ret_dict
        else:
            logger.exception(f"Exception occurred: {result.status_code}")
            result.raise_for_status()

    def get_last_listened(self, after_unix_timestamp: int, max_range: int):
        url= f'https://api.spotify.com/v1/me/player/recently-played?limit={max_range}&after={after_unix_timestamp}'
        headers = self._get_auth_header()
        result = get(url=url, headers=headers)
        if result.status_code == OK:
            logger.info(f'Last played songs with limit: {max_range} and after: {after_unix_timestamp} received.')
            ret = json.loads(result.content)
            return ret
        else:
            logger.exception(f"Exception occurred: {result.status_code}")
            result.raise_for_status()

if __name__ == "__main__":
    spotify = Spotify()
    spotify.get_user_token('playlist-read-private, user-read-currently-playing, user-read-recently-played')
    print(spotify.get_information_current_song())
    # while True:
    #     print(spotify.get_information_current_song())
    #     time.sleep(5)
    # art_id = spotify.search_artist("Babymetal")["id"]
    # songs = spotify.get_song_by_artist_id(art_id)
    # print(songs)
    #
    # for index, song in enumerate(songs):
    #     print(f"{index+1}: {song['name']}")
