import pandas as pd
from tqdm import tqdm
import os
from joblib import Parallel, delayed
import multiprocessing
from fingerprint_generator import fingerprint, read_audio  # Assuming you have these functions

# Function to process a single track and return fingerprints
def process_track(row, songDatabasePath):
    artist = row['artists']
    track = row['track_name']
    songID = row['SongID']
    expected_filename = f"{songID}.mp3"
    
    fullPath = os.path.join(songDatabasePath, expected_filename)
    
    if os.path.exists(fullPath):
        print(f"Processing {songID}")
        channels, samplerate = read_audio(fullPath)
        fingerprints = set()
        for channel in channels:
            code = fingerprint(channel, Fs=samplerate)
            fingerprints |= set(code)
        
        # Prepare data for DataFrame
        return [(row['SongID'], artist, track, hash, offset) for hash, offset in fingerprints]
    return []

# Function to make database with parallel processing
def make_database_parallel():
    songDatabasePath = '../preprocessing/mp3s_new'
    databaseFilePath = './optimized_audio_fingerprint_database.csv'
    column_names = ['SongID', 'Artist', 'Track', 'Hash', 'Offset']
    x_csv_path = '../preprocessing/SONGS_DB.csv'
    
    tracks_df = pd.read_csv(x_csv_path)
    num_cores = multiprocessing.cpu_count()

    # Process each track in parallel
    results = Parallel(n_jobs=num_cores)(
        delayed(process_track)(row, songDatabasePath) for _, row in tqdm(list(tracks_df.iterrows())[:101])
    )

    # Flatten list of lists
    fingerprints = [fp for sublist in results for fp in sublist]
    
    # Write to CSV in bulk
    fingerprints_df = pd.DataFrame(fingerprints, columns=column_names)
    fingerprints_df.to_csv(databaseFilePath, mode='w', header=True, index=False)

if __name__ == "__main__":
    make_database_parallel()
    print("Database created.")
