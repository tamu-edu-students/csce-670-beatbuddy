import pandas as pd
import logging
import lyricsgenius
import os
import time
from requests.exceptions import Timeout
genius = lyricsgenius.Genius('7AWYsIIhsPFR3V-cXmALXlDbOc3fq1BXqV3rsdEtzBwGfVjIFAmy6dUBPxQM1i9z', timeout=10, sleep_time=0.5, verbose=False)

def get_lyrics(track_name, artist, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Attempt to get the song object
            song = genius.search_song(track_name, artist)
            if song:
                return song.lyrics
            break
        except Timeout as e:
            logging.warning(f"Timeout occurred for {artist} - {track_name}: {e}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying
            retry_count += 1

    logging.error(f"Failed to fetch lyrics for {artist} - {track_name} after {max_retries} retries.")
    return None

def search_and_save_lyrics(df):
    for _, row in df.iterrows():
        songId = row['SongID']
        print(songId)
        artist = row['artists']
        track_name = row['track_name']
        search_query = f"{artist} {track_name}"
        logging.info(f"Fetching lyrics for: {search_query}")
        
        lyrics = get_lyrics(track_name, artist)
        
        if lyrics and not lyrics.startswith("Sorry"):
            # Format filename as 'artist_track.txt'
            filename = f"{songId}.txt"  # Replace any forward slashes to avoid directory issues
            # Ensure a directory exists for the lyrics files
            os.makedirs('./lyrics', exist_ok=True)
            
            # Define the file path
            file_path = os.path.join('./lyrics', filename)
            
            # Save lyrics to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(lyrics)
                logging.info(f"Saved lyrics for: {search_query} to {file_path}")
        else:
            logging.error(f"Lyrics not found for: {search_query}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dataset_path = "updated_dataset_with_youtube_urls.csv"
    df = pd.read_csv(dataset_path)
    search_and_save_lyrics(df[0:])
