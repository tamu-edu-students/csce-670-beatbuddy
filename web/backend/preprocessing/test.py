import pandas as pd
import os

# Load the CSV file
csv_file_path = 'updated_dataset_with_youtube_urls.csv'  # Replace with your actual file path
df = pd.read_csv(csv_file_path)

# # Rename the 'Unnamed: 0' column to 'song_id' and set a sequence from 0 to length of the DataFrame
df.rename(columns={'song_id': 'SongID'}, inplace=True)
df['SongID'] = range(len(df))


# Save the DataFrame back to CSV
df.to_csv(csv_file_path, index=False)
