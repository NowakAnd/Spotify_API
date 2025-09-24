"""
Authentication server for handling Spotify OAuth2 flow.

This module provides functionality for obtaining user authorization
and handling the OAuth2 callback from Spotify.
"""

import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from requests_oauthlib import OAuth2Session

from definitions import REDIRECT_URI, AUTH_URL, CLI_ID
from logger import logger

class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        """Override default logging to use our logger."""
        logger.info("%s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:
        """Handle GET request from Spotify OAuth callback."""
        try:
            # Parse query parameters
            query_components = parse_qs(self.path[10:])  # Remove leading '/?'
            logger.debug(f"Received callback with query params: {query_components}")
            
            # Check for error response from Spotify
            if 'error' in query_components:
                error = query_components.get('error', ['Unknown error'])[0]
                error_desc = query_components.get('error_description', [''])[0]
                logger.error(f"Spotify authorization error: {error} - {error_desc}")
                self.send_error(400, f"Authorization failed: {error}")
                return
                
            # Check for authorization code
            if 'code' in query_components:
                self.server.code = query_components['code']
                logger.info("Successfully received authorization code")
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(
                    b'<html><body>'
                    b'<h1>Successfully authorized!</h1>'
                    b'<p>You can close this window now.</p>'
                    b'</body></html>'
                )
            else:
                logger.warning("Received callback without code parameter")
                self.send_error(400, "Missing authorization code")
                
        except Exception as e:
            logger.exception("Error processing callback:")
            self.send_error(500, f"Internal server error: {str(e)}")

class AuthServer:
    """Handles Spotify OAuth2 authentication flow.
    
    This class manages the OAuth2 authorization code flow with Spotify's API,
    including generating authorization URLs and handling the callback.
    
    Args:
        scope: Space-separated string of Spotify authorization scopes
        host: Hostname for the callback server (default: 127.0.0.1)
        port: Port for the callback server (default: 3000)
    """
    
    def __init__(self, scope: str, host: str = "127.0.0.1", port: int = 3000) -> None:
        """Initialize the AuthServer with the specified scopes and server configuration."""
        self.scope = scope
        self.host = host
        self.port = port
        self._validate_scopes()
        
    def _validate_scopes(self) -> None:
        """Validate that the provided scopes are valid Spotify scopes."""
        valid_scopes = {
            'user-read-private', 'user-read-email', 'user-read-playback-state',
            'user-modify-playback-state', 'user-read-currently-playing',
            'user-read-recently-played', 'user-read-playback-position',
            'user-top-read', 'playlist-read-private', 'playlist-read-collaborative',
            'streaming', 'app-remote-control', 'user-library-read',
            'user-library-modify', 'user-follow-read', 'user-follow-modify'
        }
        
        for scope in self.scope.split():
            if scope not in valid_scopes:
                logger.warning(f"Unknown scope: {scope}")

    def get_auth_url(self) -> str:
        """
        Generate the Spotify authorization URL.
        
        Returns:
            str: The URL to redirect users to for Spotify authorization
            
        Raises:
            RuntimeError: If there's an error generating the authorization URL
        """
        try:
            o2auth = OAuth2Session(
                client_id=CLI_ID,
                scope=self.scope,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = o2auth.authorization_url(AUTH_URL)
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate auth URL: {str(e)}")
            raise RuntimeError(f"Failed to generate authorization URL: {str(e)}")

    def callback(self, timeout: int = 120) -> str:
        """
        Handle the OAuth2 authorization code flow.
        
        This method will:
        1. Open the user's default browser to the Spotify authorization page
        2. Start a local HTTP server to handle the OAuth2 callback
        3. Wait for the user to complete the authorization
        4. Return the authorization code
        
        Args:
            timeout: Maximum time in seconds to wait for authorization (default: 120)
            
        Returns:
            str: The authorization code from Spotify
            
        Raises:
            RuntimeError: If the authorization process fails or times out
            TimeoutError: If the authorization process takes longer than the specified timeout
        """
        import time
        from threading import Thread
        
        class ServerThread(Thread):
            """Helper class to run the HTTP server in a separate thread."""
            def __init__(self, host: str, port: int):
                super().__init__(daemon=True)
                self.host = host
                self.port = port
                self.server = None
                self.error = None
                
            def run(self):
                try:
                    self.server = HTTPServer((self.host, self.port), CallbackHandler)
                    self.server.timeout = 1  # Short timeout to allow for keyboard interrupt
                    while not hasattr(self.server, 'code') and not hasattr(self, 'stop_flag'):
                        self.server.handle_request()
                except Exception as e:
                    self.error = e
                finally:
                    if self.server:
                        self.server.server_close()
        
        try:
            # Start the server in a separate thread
            server_thread = ServerThread(self.host, self.port)
            
            # Get the authorization URL and open the browser
            auth_url = self.get_auth_url()
            logger.info(f"Initiating OAuth2 flow. Opening browser to: {auth_url}")
            webbrowser.open(auth_url)
            server_thread.run()
            
            # Wait for the authorization code with timeout
            logger.info(f"Waiting for authorization on http://{self.host}:{self.port}")
            start_time = time.time()
            
            while not hasattr(server_thread, 'server') or not hasattr(server_thread.server, 'code'):
                if server_thread.error:
                    raise RuntimeError(f"Server error: {server_thread.error}")
                    
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Authorization timed out after {timeout} seconds")
                    
                time.sleep(0.1)
            
            # Get the authorization code
            auth_code = server_thread.server.code
            if isinstance(auth_code, list):
                auth_code = auth_code[0]
                
            logger.info("Successfully obtained authorization code")
            return auth_code
            
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"Authorization failed: {str(e)}") from e
            
        finally:
            # Ensure the server thread is stopped
            if 'server_thread' in locals() and server_thread.is_alive():
                server_thread.stop_flag = True
                server_thread.join(timeout=1)
