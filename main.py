import os
import base64
import json
from re import search

from dotenv import load_dotenv
from requests import post, get
from http.client import OK

#CREATE .env WHERE YOU ARE GOING TO STORE CLIENT_ID AND SECRET_ID FROM SPOTIFY API

load_dotenv()
cli_id = os.getenv("CLIENT_ID")
secret_id = os.getenv("CLIENT_SECRET")


class Spotify:
    def __init__(self, client_id, client_secret) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

    def get_token(self) -> str:
        auth_string : str = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = 'https://accounts.spotify.com/api/token'
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form = {
            "grant_type": "client_credentials"
        }
        result = post(url, headers=headers, data=form)
        if result.status_code == OK:
            json_result = json.loads(result.content)
            return json_result['access_token']
        else:
            raise Exception(f"Non-success status code: {result.status_code}")

    def _get_auth_header(self) -> dict[str:str]:
        return {"Authorization": "Bearer " + self.token}

    def search_artist(self, artist_name: str) -> dict:
        url = 'https://api.spotify.com/v1/search?'
        headers = self._get_auth_header()
        query = f"q={artist_name}&type=artist&limit=1"

        query_url = url + query
        result = get(query_url, headers=headers)
        if result.status_code == OK:
            ret = json.loads(result.content)["artists"]["items"]
            return ret[0]
        else:
            result.raise_for_status()

    def get_song_by_artist_id(self, artist_id: str):
        url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
        headers = self._get_auth_header()
        result = get(url, headers=headers)
        if result.status_code == OK:
            ret = json.loads(result.content)["tracks"]
            return ret
        else:
            result.raise_for_status()




if __name__ == "__main__":
    spotify = Spotify(cli_id, secret_id)
    art_id = spotify.search_artist("Babymetal")["id"]
    songs = spotify.get_song_by_artist_id(art_id)

    for index, song in enumerate(songs):
        print(f"{index+1}: {song['name']}")
