import time
import pandas as pd

from definitions import SONGS_CSV_PATH, SONG_ACCEPTANCE_TIME_MS
from spotify import Spotify
from logger import logger

def add_new_song_to_csv(dataframe: pd.DataFrame, song_id: str, song: str, artists: list[str]) -> None:
    dataframe.loc[song_id] = song, artists, 1
    dataframe.to_csv(SONGS_CSV_PATH)

def update_song_counter(dataframe: pd.DataFrame, song_id: str) -> None:
    counter = dataframe.loc[song_id, 'Count']
    dataframe.loc[song_id, 'Count'] = counter + 1
    dataframe.to_csv(SONGS_CSV_PATH)

if __name__ == '__main__':
    spotify = Spotify()
    if not spotify.get_user_token('user-read-currently-playing'):
        raise Exception("Token not generated")
    logger.info("Token generated")
    save_status = False
    while True:
        time.sleep(5)
        current_song: dict = spotify.get_information_current_song()
        logger.info(f"Current song received: {current_song}")
        if current_song is None:
            logger.info("Current song is None")
            continue
        curr_progress_ms, curr_artists, curr_song, curr_song_id, curr_play_status = current_song.values()
        if not curr_play_status:
            logger.info("Current song is not playing")
            continue
        if curr_progress_ms >= SONG_ACCEPTANCE_TIME_MS and not save_status:
            df = pd.read_csv(SONGS_CSV_PATH, index_col='Song_ID')
            if curr_song_id not in df.index:
                logger.info("New song added to csv")
                add_new_song_to_csv(df, curr_song_id, curr_song, curr_artists)
            else:
                logger.info("Song counter updated")
                update_song_counter(df, curr_song_id)

            saved_song_id = curr_song_id
            save_status = True

        #Reapeat song case
        if save_status and saved_song_id == curr_song_id and curr_progress_ms <= SONG_ACCEPTANCE_TIME_MS:
            logger.info("Song repeated")
            save_status = False

        #Next song case
        if save_status and saved_song_id != curr_song_id:
            logger.info("Next song")
            save_status = False


