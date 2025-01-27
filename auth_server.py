import webbrowser

from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from requests_oauthlib import OAuth2Session

from definitions import REDIRECT_URI, AUTH_URL, CLI_ID

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(self.path[2:])
        if 'allback?code' in query_components:
            self.server.code = query_components['allback?code']
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

class AuthServer:
    def __init__(self, scope: str) -> None:
        self.scope = scope

    def get_auth_url(self) -> str:
        """
        Get url of Spotify authentication page with desired scopes.
        :return: Authentication URL
        """
        o2auth = OAuth2Session(CLI_ID, scope=self.scope, redirect_uri=REDIRECT_URI)
        auth_url, _ = o2auth.authorization_url(AUTH_URL)
        return auth_url

    def callback(self) -> str:
        """
        Opens web browser to log to user account and retrieve code required to access user token
        :return: Code token
        """
        webbrowser.open(self.get_auth_url())
        server = HTTPServer(('localhost', 3000), CallbackHandler)
        server.handle_request()
        return server.code
