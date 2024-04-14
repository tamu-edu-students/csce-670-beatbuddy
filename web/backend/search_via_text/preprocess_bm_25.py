from rank_bm25 import BM25Okapi
import pickle
import os  # Required for listing files in a directory
import re

def preprocess(document):
    document = document.lower()
    tokens = re.sub(r'\[.*?\]|[\n\r\t\f\v]|(\\u[0-9A-Fa-f]+)|[^\w\s]', ' ', document).split()
    tokens = [token for token in tokens if re.search('[a-zA-Z]', token)]
    return tokens
# Assuming 'preprocessing' is a module you have that contains the 'preprocess' function
# If 'preprocess' is a function within the same script, you can import it directly

path = "../preprocessing/lyrics"  # Adjust this path to the correct directory containing your documents

documents = []
# Iterate through each file in the specified directory
for filename in os.listdir(path):
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):  # Check if it's a file
        with open(file_path, 'r', encoding='utf-8') as f:  # Ensure correct handling of file encoding
            document = f.read()
            documents.append(document)

def save_bm25_model(filepath='bm25.pkl'):
    # Tokenize and preprocess each document in the corpus
    tokenized_corpus = [preprocess(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    # Save the BM25 model to the specified filepath
    with open(filepath, 'wb') as file:
        pickle.dump(bm25, file)

# Call the function to save the BM25 model
save_bm25_model()
