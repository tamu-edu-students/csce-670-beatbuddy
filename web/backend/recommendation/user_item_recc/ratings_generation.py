import pandas as pd
from sklearn.model_selection import train_test_split
import random
import numpy as np

def generate_user_ratings(data_path):
    data = pd.read_csv(data_path)
    sorted_df = data.sort_values(by="popularity", ascending=False).head(5000)

    genres = list(sorted_df.track_genre.unique())
    num_users = 2000
    songs = list(sorted_df.track_id.unique())
    num_songs = sorted_df.track_id.nunique()

    ratings = {user_id: {song_id: 0 for song_id in songs} for user_id in range(num_users)}

    for user_id in range(num_users): 
        zero_rating = random.randint(20, 30)
        prob_zero_rating = zero_rating / 100
        
        # Calculate the number of songs to assign value 0
        num_zero_value = int(num_songs * prob_zero_rating)

        # Randomly select songs to assign value 0
        songs_to_zero_value = random.sample(songs, num_zero_value)
        
        remaining_songs = [item for item in songs if item not in songs_to_zero_value]
        
        remaining_df = sorted_df[sorted_df['track_id'].isin(remaining_songs)]
        remaining_unique_genres = list(remaining_df.track_genre.unique())
        
        genre_counts = remaining_df.track_genre.value_counts()
        
        total_tracks = len(remaining_df)
        cumulative_count = 0
        selected_genres = []
        for genre, count in genre_counts.items():
            cumulative_count += count
            if cumulative_count <= 0.6 * total_tracks:
                selected_genres.append(genre)
            else:
                break

        liking_genre_df = remaining_df[remaining_df['track_genre'].isin(selected_genres)]

        unique_liking_songs = list(liking_genre_df.track_id.unique())
        random.shuffle(unique_liking_songs)
        num_songs_rating_4 = len(unique_liking_songs) // 2
        num_songs_rating_5 = len(unique_liking_songs) - num_songs_rating_4
        liking_ratings = [4] * num_songs_rating_4 + [5] * num_songs_rating_5
        random.shuffle(liking_ratings)
        liking_song_ratings = dict(zip(unique_liking_songs, liking_ratings))

        for song_id, rating in liking_song_ratings.items():
            ratings[user_id][song_id] = rating
            
        non_selected_genres = list(set(list(remaining_unique_genres)) - set(selected_genres))

        
        non_liking_genre_df = remaining_df[remaining_df['track_genre'].isin(non_selected_genres)]

        unique_disliking_songs = list(non_liking_genre_df.track_id.unique())
        random.shuffle(unique_disliking_songs)
        num_songs = len(unique_disliking_songs)
        num_songs_rating_3 = num_songs // 2
        num_songs_rating_2 = (num_songs - num_songs_rating_3) // 2
        num_songs_rating_1 = num_songs - num_songs_rating_3 - num_songs_rating_2

        # Assign ratings
        disliking_ratings = np.concatenate((np.full(num_songs_rating_3, 3),
                                np.full(num_songs_rating_2, 2),
                                np.full(num_songs_rating_1, 1)))

        # Shuffle the ratings array to randomize the assignment
        np.random.shuffle(disliking_ratings)

        # Create a dictionary to map song IDs to ratings
        disliking_song_ratings = dict(zip(unique_disliking_songs, disliking_ratings))

        for song_id, rating in disliking_song_ratings.items():
            ratings[user_id][song_id] = rating
        
        for song_id in songs_to_zero_value:
            ratings[user_id][song_id] = 0

    ratings_df = pd.DataFrame.from_dict(ratings, orient='index')
    # ratings_df.to_excel("ratings.xlsx", engine="openpyxl")
    return ratings_df


generate_user_ratings("./web/backend/preprocessing/updated_dataset_with_youtube_urls.csv")
