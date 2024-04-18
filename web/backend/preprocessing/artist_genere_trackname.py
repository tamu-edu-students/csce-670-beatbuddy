import csv
import os

# Define the path to the CSV file and the directory containing the text files
csv_file_path = 'web/backend/preprocessing/updated_dataset_with_youtube_urls.csv'
txt_file_directory = 'web/backend/preprocessing/lyrics'
# Open the CSV file and read data
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
        song_id = row['SongID']
        if int(song_id) > 11172:
            break
        track_name = row['track_name']
        album_name=row['album_name']
        artist_name = row['artists']
        track_genre=row['track_genre']
        all_info_str=" "+str(track_name)+" "+str(album_name)+" "+str(artist_name)+" "+str(track_genre)

        # Construct the filename from songID
        txt_file_path = os.path.join(txt_file_directory, f'{song_id}.txt')
        # Check if the file exists
        if os.path.exists(txt_file_path):
            #Open the text file and append the track name and artist name
            with open(txt_file_path, 'a', encoding='utf-8') as file:
                file.write(all_info_str)
        else:
            print(f"No file found for songID {song_id}")
           
