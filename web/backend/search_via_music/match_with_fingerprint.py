import pandas as pd
import fingerprint as fp
from itertools import groupby
from operator import itemgetter
import pandas as pd
from time import time

def find_matches_in_csv(hashes, csv_file_path = "../preprocessing/audio_fingerprint_database.csv", batch_size=1000):
    # Load the CSV data
    df = pd.read_csv(csv_file_path)
    batch_size = 1000
    # Prepare the mapper from your hashes
    mapper = {}
    for hsh, offset in hashes:
        upper_hash = hsh.upper()
        if upper_hash in mapper:
            mapper[upper_hash].append(offset)
        else:
            mapper[upper_hash] = [offset]
    values = list(mapper.keys())
    
    # Initialize results and deduplication dict
    results = []
    dedup_hashes = {}
    t = time()
    # Iterate through the DataFrame
    for index in range(0, len(hashes), batch_size):
        batch_hashes = values[index:index + batch_size]
        db_matches = df[df['Hash'].str.upper().isin(batch_hashes)]
        
        for _, row in db_matches.iterrows():
            hsh, sid, db_offset = row['Hash'].upper(), row['SongID'], row['Offset']
            if sid not in dedup_hashes.keys():
                dedup_hashes[sid] = 1
            else:
                dedup_hashes[sid] += 1

            for song_sampled_offset in mapper[hsh]:
                results.append((sid, db_offset - song_sampled_offset))

    query_time = time() - t
    print(f"Query time: {query_time}")
    t = time()
    results = align_matches(results, dedup_hashes, len(hashes), df)
    print(f"Alignment time: {time() - t}")
    return results


def align_matches(matches, dedup_hashes, queried_hashes, df_songs, topn=5, default_fs=44100, window_size=4096, overlap_ratio=0.5):
    sorted_matches = sorted(matches, key=itemgetter(0, 1))
    counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=itemgetter(0, 1))]
    
    songs_matches = sorted(
        [max(list(group), key=itemgetter(2)) for key, group in groupby(counts, key=itemgetter(0))],
        key=itemgetter(2), reverse=True
    )
    songs_result = []
    for song_id, offset, _ in songs_matches[:min(len(songs_matches), topn)]:  # Consider topn elements in the result
        song_info = df_songs[df_songs['SongID'] == song_id].iloc[0]
        nseconds = round(float(offset) / default_fs * window_size * overlap_ratio, 5)
        hashes_matched = dedup_hashes[song_id]

        song_dict = {
            'SongID': song_id,
            'InputHashes': queried_hashes,
            'HashesMatched': hashes_matched,
            'InputConfidence': round(hashes_matched / queried_hashes, 2),
            'Offset': offset,
            'OffsetSecs': nseconds,
        }
        print(song_dict)
        songs_result.append(song_dict)

    return songs_result


def main(channels, samplerate):
    hashes = set()
    for channel in channels:
        fingerprints = fp.fingerprint(channel, Fs=samplerate)  # Assuming fingerprint is a defined function
        hashes |= set(fingerprints)
    # Convert the set of hashes to a string to store in CSV
    return find_matches_in_csv(hashes)

    