"""
This module provides the SongTracker class for managing song tracking and CSV operations.
"""
from pathlib import Path
from typing import Optional
import pandas as pd
from logger import logger

class SongTracker:
    """Handles tracking and updating song information in the CSV file."""
    
    def __init__(self, csv_path: str) -> None:
        """Initialize the SongTracker with the path to the CSV file.
        
        Args:
            csv_path: Path to the CSV file for storing song data
        """
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        self._initialize_csv()
    
    def _initialize_csv(self) -> None:
        """Initialize or load the CSV file with proper error handling."""
        try:
            if not self.csv_path.exists():
                self._create_new_csv()
            else:
                self._load_existing_csv()
        except Exception as e:
            logger.error(f"Failed to initialize CSV at {self.csv_path}: {e}")
            raise

    def _create_new_csv(self) -> None:
        """Create a new CSV file with the required structure."""
        self.df = pd.DataFrame(columns=['Song', 'Artists', 'Count'])
        self.df.index.name = 'Song_ID'
        self._save_csv()
        logger.info(f"Created new song tracking file at {self.csv_path}")

    def _load_existing_csv(self) -> None:
        """Load an existing CSV file with validation."""
        try:
            self.df = pd.read_csv(self.csv_path, index_col='Song_ID')
            required_columns = {'Song', 'Artists', 'Count'}
            if not required_columns.issubset(self.df.columns):
                raise ValueError(f"CSV file is missing required columns: {required_columns - set(self.df.columns)}")
            logger.info(f"Loaded existing song tracking file with {len(self.df)} entries")
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            # Create backup before potentially overwriting
            self._backup_csv()
            self._create_new_csv()

    def _backup_csv(self) -> None:
        """Create a backup of the current CSV file."""
        backup_path = self.csv_path.with_suffix('.bak' + self.csv_path.suffix)
        try:
            if self.df is not None:
                self.df.to_csv(backup_path)
                logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")

    def _save_csv(self) -> None:
        """Save the DataFrame to CSV with error handling and retries."""
        if self.df is None:
            logger.error("Cannot save: DataFrame is None")
            return
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure the directory exists
                self.csv_path.parent.mkdir(parents=True, exist_ok=True)
                # Save with index (Song_ID)
                self.df.to_csv(self.csv_path)
                return  # Success
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"Failed to save CSV after {max_retries} attempts: {e}")
                    self._backup_csv()
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying...")

    def add_song(self, song_id: str, song_name: str, artists: list[str]) -> None:
        """Add a new song or update an existing one.
        
        Args:
            song_id: Unique identifier for the song
            song_name: Name of the song
            artists: List of artist names
        """
        if not all([song_id, song_name, artists]):
            raise ValueError("song_id, song_name, and artists are required")
            
        if song_id in self.df.index:
            self.update_song_counter(song_id)
            return
            
        try:
            self.df.loc[song_id] = [song_name, artists, 1]
            self._save_csv()
            logger.info(f"Added new song: {song_name} by {', '.join(artists)}")
        except Exception as e:
            logger.error(f"Failed to add song {song_name}: {e}")
            raise

    def update_song_counter(self, song_id: str) -> None:
        """Increment the play counter for a song.
        
        Args:
            song_id: ID of the song to update
        """
        if self.df is None:
            logger.error("Cannot update counter: DataFrame is not initialized")
            return
            
        if song_id not in self.df.index:
            logger.warning(f"Song ID {song_id} not found for counter update")
            return
            
        try:
            current_count = self.df.at[song_id, 'Count']
            self.df.at[song_id, 'Count'] = current_count + 1
            self._save_csv()
            logger.debug(f"Updated counter for song ID {song_id} to {current_count + 1}")
        except Exception as e:
            logger.error(f"Failed to update counter for song ID {song_id}: {e}")
            raise
