import pandas as pd
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
import preprocess_bm_25  

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

def encode(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True, padding='max_length')
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().cpu().numpy()  # [CLS] token embedding

path = "web/backend/preprocessing/lyrics" 
documents = {}

# Iterate through each file in the specified directory
for filename in os.listdir(path):
    doc_id = int(filename.split(".")[0])
    print(doc_id)
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):  # Check if it's a file
        with open(file_path, 'r', encoding='utf-8') as f:  # Ensure correct handling of file encoding
            document = f.read()
            documents[doc_id]=encode(document)
    

import pickle
with open("bert_embeddings.pkl", 'wb') as file:
        pickle.dump(documents, file)

with open("bert_model.pkl", 'wb') as file:
        pickle.dump(model, file)

with open("bert_tokenizer.pkl", 'wb') as file:
        pickle.dump(tokenizer, file)
