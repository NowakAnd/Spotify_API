"""
Spotify Song Tracker

This script tracks the currently playing songs on Spotify and maintains a count of plays
in a CSV file. It handles song changes, repeats, and various error conditions.
"""
import time
import signal
import sys
from typing import Optional

from definitions import (
    SONGS_CSV_PATH,
    SONG_ACCEPTANCE_TIME_MS,
    CLI_ID,
    SECRET_ID,
    REDIRECT_URI,
    LOOP_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS
)
from models import AuthSpotify
from spotify import Spotify
from song_tracker import SongTracker
from logger import logger

class SpotifyTracker:
    """Main class for tracking Spotify playback."""
    
    def __init__(self):
        """Initialize the Spotify tracker with configuration."""
        self.running = True
        self.song_tracker = SongTracker(SONGS_CSV_PATH)
        self.spotify = self._setup_spotify()
        self.current_song_id: Optional[str] = None
        self.save_status = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    @staticmethod
    def _setup_spotify() -> Spotify:
        """Set up and authenticate with the Spotify API."""
        scopes = ["user-read-currently-playing"]
        auth = AuthSpotify(
            cli_id=CLI_ID,
            secret_id=SECRET_ID,
            redirect_uri=REDIRECT_URI,
            scope=scopes
        )
        return Spotify(auth_spotify=auth, user=True)
    
    def _handle_shutdown(self):
        """Handle shutdown signals gracefully."""
        logger.info("Shutting down gracefully...")
        self.running = False
    
    def _process_current_song(self):
        """Process the currently playing song."""
        try:
            current_song = self.spotify.get_information_current_song()
            
            if not current_song or not current_song.play_status:
                return True
                
            # Handle new song
            if current_song.progress_ms >= SONG_ACCEPTANCE_TIME_MS and not self.save_status:
                self._handle_new_song(current_song)
                return True
                
            # Handle song repeat case
            if (self.save_status and 
                self.current_song_id == current_song.song_id and 
                current_song.progress_ms <= SONG_ACCEPTANCE_TIME_MS):
                self._handle_repeated_song(current_song)
                return True
                
            # Handle next song case
            if self.save_status and self.current_song_id != current_song.song_id:
                self._handle_next_song()
                return True
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing current song: {e}")
            return False
    
    def _handle_new_song(self, current_song):
        """Handle a new song that's being played."""
        logger.info(f"New song detected: {current_song.song_name} by {', '.join(current_song.artists)}")
        self.song_tracker.add_song(
            song_id=current_song.song_id,
            song_name=current_song.song_name,
            artists=current_song.artists
        )
        self.current_song_id = current_song.song_id
        self.save_status = True
    
    def _handle_repeated_song(self, current_song):
        """Handle when the current song is repeated."""
        logger.info(f"Song repeated: {current_song.song_name}")
        self.song_tracker.update_song_counter(current_song.song_id)
        self.save_status = False
    
    def _handle_next_song(self):
        """Handle transition to a new song."""
        logger.info("Next song detected, resetting save status")
        self.save_status = False
    
    def run(self):
        """Run the main tracking loop."""
        logger.info("Starting Spotify Song Tracker...")
        
        consecutive_errors = 0
        
        while self.running:
            try:
                if self._process_current_song():
                    consecutive_errors = 0
                else:
                    # Only increment error counter if we're not in the middle of processing a song
                    if not self.save_status:
                        consecutive_errors += 1
                        
                        if consecutive_errors >= 5:
                            logger.warning(
                                f"Multiple consecutive errors ({consecutive_errors}). "
                                "Potential issue with Spotify API or connection."
                            )
                
                time.sleep(LOOP_DELAY_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                consecutive_errors += 1
                time.sleep(RETRY_DELAY_SECONDS)
                
                if consecutive_errors >= MAX_RETRIES:
                    logger.error("Maximum retry attempts reached. Shutting down.")
                    break
        
        logger.info("Spotify Song Tracker stopped")

def main():
    """Entry point for the application."""
    try:
        tracker = SpotifyTracker()
        tracker.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
