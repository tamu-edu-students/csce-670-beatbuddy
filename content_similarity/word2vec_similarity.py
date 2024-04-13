from gensim.models import Word2Vec
import pandas as pd
import numpy as np
import os

path = "../preprocessing/lyrics"  # Adjust this path to the correct directory containing your documents

lyrics = []
# Iterate through each file in the specified directory
for filename in os.listdir(path):
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):  # Check if it's a file
        with open(file_path, 'r', encoding='utf-8') as f:  # Ensure correct handling of file encoding
            document = f.read()
            lyrics.append(document)

# Train a Word2Vec model on the aggregated lyrics
model = Word2Vec(sentences=df['lyrics'].tolist(), vector_size=100, window=5, min_count=1, workers=4)

# Function to vectorize a song's lyrics
def vectorize_song(lyrics, model):
    vector = np.mean([model.wv[word] for word in lyrics if word in model.wv], axis=0)
    return vector

# Vectorize all songs
df['vector'] = df['lyrics'].apply(lambda x: vectorize_song(x, model))

# Example function to recommend songs based on a given song's index
def recommend_songs(song_index, df, top_n=5):
    target_vector = df.iloc[song_index]['vector']
    df['similarity'] = df['vector'].apply(lambda x: np.dot(target_vector, x) / (np.linalg.norm(target_vector) * np.linalg.norm(x)))
    recommendations = df.sort_values(by='similarity', ascending=False).head(top_n + 1)
    return recommendations.iloc[1:] # exclude the song itself from its recommendations

# Assuming you want recommendations based on the first song in your DataFrame
recommendations = recommend_songs(0, df, top_n=5)
print(recommendations)
