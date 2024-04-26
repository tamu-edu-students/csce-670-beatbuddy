# This code uses https://www.kaggle.com/code/electrichands/spotify-similarity-based/notebook, licensed under Apache License 2.0.


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from scipy import stats
#import matplotlib.pyplot as plt
import fasttext
from sklearn.preprocessing import StandardScaler
from annoy import AnnoyIndex

def find_outliers(dataframe, column_name):
    # Calculate Z-scores
    z_scores = stats.zscore(dataframe[column_name])
    # Define a threshold for identifying outliers
    threshold = 3
    # Get boolean array of outliers
    outliers = (z_scores > threshold) | (z_scores < -threshold)
    # Return the dataframe of outliers
    return dataframe[outliers]



def preprocess_data(df):
    df = df.sort_values(by='popularity', ascending=False)
    # Drop null values
    df = df.dropna()

    # Drop duplicates
    df.drop_duplicates('track_id', inplace=True)


    # Find outliers for each numerical column in the dataset
    numerical_columns = ['popularity', 'duration_ms', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    outliers_dict = {}

    for column in numerical_columns:
        outliers_dict[column] = find_outliers(df, column)
    
    # Print the number of outliers for each column
    for column, outliers_df in outliers_dict.items():
        print(f"{column} has {len(outliers_df)} outliers.")
    
    # Filter songs with duration over 10 minutes or below 1 minute
    #duration_outliers = df[(df['duration_min'] > 12) | (df['duration_min'] < 0.5)]

    return df

def train_model(df):
    # Combine the text columns into a single string for each row and save to a text file
    text_data = df['artists'] + ' ' + df['track_name'] + ' ' + df['album_name'] + ' ' + df['track_genre']
    text_data.to_csv('text_data.txt', index=False, header=False)


    # Train the fastText model on the text data

    model = fasttext.train_unsupervised('text_data.txt', model='skipgram')

    return model

def get_mean_embedding(words_list, model):
    embeddings = [model.get_word_vector(word) for word in words_list]
    mean_embedding = np.mean(embeddings, axis=0)
    return mean_embedding

# Function to handle multiple artists and get their mean embedding
def get_artists_embedding(artists, model):
    # Split the artists string into individual artists
    artists_list = artists.split(';')
    # Get the mean embedding for the list of artists
    return get_mean_embedding(artists_list, model)


def get_track_embedding(track, model):
    # Get the embeddings as before
    artists_embedding = get_artists_embedding(track['artists'], model)
    track_name_embedding = get_mean_embedding(track['track_name'].split(), model)
    album_name_embedding = get_mean_embedding(track['album_name'].split(), model)
    track_genre_embedding = get_mean_embedding(track['track_genre'].split(), model)

    # Get the numerical features
    numerical_features = np.array([track['popularity'], track['duration_ms'], track['danceability'], track['loudness'], track['energy'], track['speechiness'], track['instrumentalness'], track['liveness'], track['valence'], track['tempo']])



    # Normalize the numerical features to have the same scale as the embeddings
    # This step is important to ensure that the numerical features do not dominate the embeddings
    scaler = StandardScaler()
    normalized_numerical_features = scaler.fit_transform(numerical_features.reshape(-1, 1))

    # Flatten the normalized numerical features to 1D
    normalized_numerical_features = normalized_numerical_features.flatten()

    # Concatenate the embeddings and the numerical features
    final_embedding = artists_embedding + track_name_embedding + album_name_embedding + track_genre_embedding
    final_embedding = np.concatenate([final_embedding, normalized_numerical_features])

    return final_embedding

def generate_embeddings(df, model):
    df['embedding'] = df.apply(lambda x: get_track_embedding(x, model), axis=1)
    return df

def build_annoy_index(df):
    t = AnnoyIndex(len(df['embedding'][0]), 'angular')

    # Build the Annoy index
    for i, row in df.iterrows():
        t.add_item(i, row['embedding'])

    # Build the index, 10 trees are being used in this example
    t.build(10)

    return t

    
def knn_based_recommendations(index, df, t):

  if index >=5000:
    return []


  # Get the embedding of the random track
  random_track_embedding = df.loc[index, 'embedding']

  # Find the 10 nearest neighbors to the random track
  nearest_neighbors_indices = t.get_nns_by_vector(random_track_embedding, 10)

  # Get the details of the recommended tracks
  recommended_tracks = df.loc[nearest_neighbors_indices]

  return list(recommended_tracks['SongID'])

def build_knn_map(df,t):
  knn_map= {}
  for SongID in range(len(df['SongID'])):
    knn_map[SongID] = knn_based_recommendations(SongID, df, t)


  return knn_map

def preprocess_ratings_matrix(df):
   df['user_id'] = df.index
   df.set_index(['user_id'],inplace=True)
   df.drop(['Unnamed: 0'],axis=1,inplace=True)
   return df

def get_top_2_rated_SongIDs(df, ratings_list=[4, 5]):
    temp = {}
    for user_id, row in df.iterrows():
        temp[user_id] = row[row.isin(ratings_list)].index.tolist()
    return temp

def recommendations_based_on_user_ratings(user_id, df1,df2, top_2_rated_SongIDs_for_all_users, knn_map):
   top_2_rated_SongIDs_user = top_2_rated_SongIDs_for_all_users[user_id]
   res_rec_SongIDs = []
   for song_id in top_2_rated_SongIDs_user:
    neighbour_SongIDs = knn_map[song_id]
    for nei_SongID in neighbour_SongIDs:
        if nei_SongID >= 5000:
           continue
        
        if df2.iloc[user_id,nei_SongID] == 0:
           res_rec_SongIDs.append(nei_SongID)
    
    filtered_df = df1[df1['SongID'].isin(res_rec_SongIDs)]
    
    # Sort the filtered DataFrame by 'popularity' column in descending order
    sorted_df = filtered_df.sort_values(by='popularity', ascending=False)

    # Take the top 5 rows
    top_5_popular_songs = sorted_df.head(5)

    top_5_song_ids = top_5_popular_songs['SongID'].tolist()

    return top_5_song_ids
    
 


def recommendations_based_on_user_ratings_and_knn(user_id):
   songs_df = pd.read_csv('/Users/druvakumargunda/Documents/TAMU/CSCE-670/ISR-Project/web/backend/recommendation/songs_db.csv')
   ratings_df = pd.read_excel('/Users/druvakumargunda/Documents/TAMU/CSCE-670/ISR-Project/web/backend/recommendation/ratings.xlsx')
   songs_df = preprocess_data(songs_df)
   ratings_df = preprocess_ratings_matrix(ratings_df)
   model = train_model(songs_df)
   songs_df = generate_embeddings(songs_df, model)
   t = build_annoy_index(songs_df)
   knn_map_for_all_SongIDs = build_knn_map(songs_df, t)
   top_2_rated_SongIDs_for_all_users = get_top_2_rated_SongIDs(ratings_df)
   rec_SongIds = recommendations_based_on_user_ratings(user_id, songs_df, ratings_df, top_2_rated_SongIDs_for_all_users, knn_map_for_all_SongIDs)
   return rec_SongIds

rec_SongIds = recommendations_based_on_user_ratings_and_knn(100)
print(rec_SongIds)