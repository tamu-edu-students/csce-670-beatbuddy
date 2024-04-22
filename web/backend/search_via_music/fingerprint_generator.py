import hashlib
from operator import itemgetter
from typing import List, Tuple
import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import os
from time import time
import sounddevice as sd
import soundfile as sf
from tqdm import tqdm
from pydub import AudioSegment
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (binary_erosion,
                                      generate_binary_structure,
                                      iterate_structure)

from config import (CONNECTIVITY_MASK, DEFAULT_AMP_MIN,
                                    DEFAULT_FAN_VALUE, DEFAULT_FS,
                                    DEFAULT_OVERLAP_RATIO, DEFAULT_WINDOW_SIZE,
                                    FINGERPRINT_REDUCTION, MAX_HASH_TIME_DELTA,
                                    MIN_HASH_TIME_DELTA,
                                    PEAK_NEIGHBORHOOD_SIZE, PEAK_SORT)



plt.ion()  # Turns on interactive mode

def read_audio(file_name, limit = None):
    try:
        # Load the audio file with pydub
        audiofile = AudioSegment.from_file(file_name)
        # Limit the duration if specified
        if limit:
            audiofile = audiofile[:limit * 1000]
        # Extract audio data
        data = np.frombuffer(audiofile.raw_data, dtype=np.int16)
        # Reshape the data for multi-channel audio files
        channels = [data[channel::audiofile.channels] for channel in range(audiofile.channels)]
        sample_rate = audiofile.frame_rate
    except Exception as e:
        raise Exception(f"Failed to read the audio file in both pydub and wavio. pydub error: {str(e)}")

    return channels, sample_rate


def fingerprint(channel_samples, Fs= DEFAULT_FS, wsize = DEFAULT_WINDOW_SIZE, wratio = DEFAULT_OVERLAP_RATIO,fan_value = DEFAULT_FAN_VALUE, amp_min = DEFAULT_AMP_MIN) :
    # FFT the signal and extract frequency components
    arr2D = mlab.specgram(
        channel_samples,
        NFFT=wsize,
        Fs=Fs,
        window=mlab.window_hanning,
        noverlap=int(wsize * wratio))[0]

    # Apply log transform since specgram function returns linear array. 0s are excluded to avoid np warning.
    arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))

    local_maxima = get_2D_peaks(arr2D, plot=False, amp_min=amp_min)

    # return hashes
    return generate_hashes(local_maxima, fan_value=fan_value)


def get_2D_peaks(arr2D, plot = False, amp_min = DEFAULT_AMP_MIN):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generate_binary_structure.html
    struct = generate_binary_structure(2, CONNECTIVITY_MASK)

    #  And then we apply dilation using the following function
    #  http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.iterate_structure.html
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima using our filter mask
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

    # Applying erosion.
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # Boolean mask of arr2D with True at peaks (applying XOR on both matrices).
    detected_peaks = local_max != eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    freqs, times = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()

    # get indices for frequency and time
    filter_idxs = np.where(amps > amp_min)

    freqs_filter = freqs[filter_idxs]
    times_filter = times[filter_idxs]
    
    if plot:
        # scatter of the peaks
        fig, ax = plt.subplots()
        ax.imshow(arr2D)  # Assuming arr2D is defined elsewhere
        ax.scatter(times_filter, freqs_filter)  # Assuming times_filter and freqs_filter are defined
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()
        # Use block=True to make show() blocking
        plt.show(block=True)

    return list(zip(freqs_filter, times_filter))


def generate_hashes(peaks, fan_value = DEFAULT_FAN_VALUE):

    # frequencies are in the first position of the tuples
    idx_freq = 0
    # times are in the second position of the tuples
    idx_time = 1

    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    hashes = []
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):

                freq1 = peaks[i][idx_freq]
                freq2 = peaks[i + j][idx_freq]
                t1 = peaks[i][idx_time]
                t2 = peaks[i + j][idx_time]
                t_delta = t2 - t1

                if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
                    h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))

                    hashes.append((h.hexdigest()[0:FINGERPRINT_REDUCTION], t1))

    return hashes



def make_database():
    songDatabasePath = '../preprocessing/mp3s/'  # Adjusted path to be relative to the current directory
    databaseFilePath = '../preprocessing/final_audio_fingerprint_database.csv'
    column_names = ['SongID', 'Artist', 'Track', 'Hash', 'Offset']  # Columns for the database
    x_csv_path = '../preprocessing/updated_dataset_with_youtube_urls.csv'  # Path to the CSV file with track names and artists
    
    # Load track names and artists from x.csv
    tracks_df = pd.read_csv(x_csv_path)
    
    # Initialize Song ID counter

    # Check if the database CSV file already exists. If not, create it with headers.
    if not os.path.exists(databaseFilePath):
        pd.DataFrame(columns=column_names).to_csv(databaseFilePath, index=False)

    for _, row in tqdm(list(tracks_df.iterrows())[350:351]):
        artist = row['artists']
        track = row['track_name']
        expected_filename = f"{track} - {artist}.mp3"  # Construct expected filename based on track and artist
        songID = row['SongID']
        # Search for the file in the ./mp3s directory
        fullPath = os.path.join(songDatabasePath, expected_filename)
        if os.path.exists(fullPath):
            # File found, process it
            print(f"Processing {songID}")
            channels, samplerate = read_audio(fullPath)  # Assuming read_audio is a defined function
            fingerprints = set()
            for channel in channels:
                code = fingerprint(channel, Fs=samplerate)  # Assuming fingerprint is a defined function
                fingerprints |= set(code)
            
            # Save each hash with its offset to the database CSV
            for hash, offset in fingerprints:
                new_row = pd.DataFrame([[row['SongID'], artist, track, hash, offset]], columns=column_names)
                new_row.to_csv(databaseFilePath, mode='a', header=False, index=False)


if __name__ == "__main__":
    make_database()
    print("Database created.") 