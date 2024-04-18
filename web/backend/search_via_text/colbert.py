import warnings
# Ignore all warnings
warnings.simplefilter(action='ignore', category=Warning)


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

def load_pklfile(filepath):
    with open(filepath,'rb') as file:
        file1=pickle.load(file)
    return file1

# Load BM25 model and tokenizer/model for BERT
bm25_model = load_bm25_model()
tokenizer = load_pklfile("bert_tokenizer.pkl") #BertTokenizer.from_pretrained('bert-base-uncased')
model = load_pklfile("bert_model.pkl")#BertModel.from_pretrained('bert-base-uncased')
model.eval()
bert_embedding=load_pklfile("bert_embeddings.pkl")
dcms_id=load_pklfile("doc_ids.pkl")

def encode(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().cpu().numpy()  # [CLS] token embedding


def calculate_similarity(query_embeddings, doc_embeddings):
    final_scores = np.zeros(doc_embeddings.shape[0])
    for doc_idx, doc_emb in enumerate(doc_embeddings):
        sim_matrix = cosine_similarity(query_embeddings, doc_emb)
        max_sim_scores = sim_matrix.max(axis=1)
        final_scores[doc_idx] = max_sim_scores.sum()
    return final_scores


def search_documents(query, num_results=10):
    query_tokens = preprocess_bm_25.preprocess(query,False)[0]
    scores = bm25_model.get_scores(query_tokens)
    top_bm25_indices = np.argsort(scores)[::-1][:num_results]
    print(top_bm25_indices)
    path = "web/backend/preprocessing/lyrics" 
    document_ids, documents = [], []
    for idx in top_bm25_indices:
        if idx in bert_embedding:
            document_ids.append(dcms_id[idx])
            documents.append(bert_embedding[idx])
    print(document_ids)
    doc_embeddings = np.array(documents)
    query_embedding = encode(query)
    print(f"Doc_embeddings: {doc_embeddings.shape}, Query_embedding: {query_embedding.shape}")
    similarities = calculate_similarity(query_embedding, doc_embeddings)
    top_colbert_indices = np.argsort(similarities)[::-1][:num_results]  # Get top N indices based on similarity

    # Map back to song IDs using document_ids
    top_song_ids = [document_ids[i] for i in top_colbert_indices]
    print(top_song_ids)
    
    tracks_df = pd.read_csv("web/backend/preprocessing/updated_dataset_with_youtube_urls.csv")
    filtered_tracks=tracks_df[tracks_df['SongID'].isin(top_song_ids)]["track_name"]
    track_names=filtered_tracks.reindex(top_song_ids).tolist()
    return track_names
if __name__=="__main__":
    # Example usage
    query = """So many people have come and gone
    Their faces fade as the years go by
    Yet I still recall as I wander on
    As clear as the sun in the summer sky""" #
    query="Believe Me"
    most_similar_documents = search_documents(query)
    print("Most similar documents:", most_similar_documents)
