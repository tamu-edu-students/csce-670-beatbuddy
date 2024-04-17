import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
import preprocess_bm_25  # Ensure this module correctly preprocesses text for BM25

def load_bm25_model(filepath='bm25.pkl'):
    with open(filepath, 'rb') as file:
        bm25 = pickle.load(file)
    return bm25

# Load BM25 model and tokenizer/model for BERT
bm25_model = load_bm25_model()
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

def encode(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().cpu().numpy()  # [CLS] token embedding

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(query_embeddings, doc_embeddings):
    final_scores = np.zeros(doc_embeddings.shape[0])
    for doc_idx, doc_emb in enumerate(doc_embeddings):
        sim_matrix = cosine_similarity(query_embeddings, doc_emb)
        max_sim_scores = sim_matrix.max(axis=1)
        final_scores[doc_idx] = max_sim_scores.sum()
    return final_scores


def search_documents(query, num_results=10):
    query_tokens = preprocess_bm_25.preprocess(query)
    scores = bm25_model.get_scores(query_tokens)
    print(scores)
    top_bm25_indices = np.argsort(scores)[::-1][:num_results]
    print(top_bm25_indices)
    path = "../preprocessing/lyrics"
    document_ids, documents = [], []
    for idx in top_bm25_indices:
        filename = f"{idx}.txt"
        if os.path.exists(os.path.join(path, filename)):
            with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                document_ids.append(idx)  # Keep track of document IDs
                documents.append(f.read())  # Directly read document content
    
    doc_embeddings = np.array([encode(doc) for doc in documents])
    query_embedding = encode(query)
    print(f"Doc_embeddings: {doc_embeddings.shape}, Query_embedding: {query_embedding.shape}")
    similarities = calculate_similarity(query_embedding, doc_embeddings)
    top_colbert_indices = np.argsort(similarities)[::-1][:num_results]  # Get top N indices based on similarity

    # Map back to song IDs using document_ids
    top_song_ids = [document_ids[i] for i in top_colbert_indices]
    
    tracks_df = pd.read_csv("../preprocessing/updated_dataset_with_youtube_urls.csv")
    filtered_tracks = tracks_df[tracks_df['SongID'].isin(top_song_ids)]
    track_names = filtered_tracks['track_name'].tolist()
    return track_names[:num_results]

# Example usage
query = "Caught the air in your woven mouth"
most_similar_documents = search_documents(query)
print("Most similar documents:", most_similar_documents)
