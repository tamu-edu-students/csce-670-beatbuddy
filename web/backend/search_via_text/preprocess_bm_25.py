from rank_bm25 import BM25Okapi
import pickle
import os  # Required for listing files in a directory
import re

from nltk.stem import PorterStemmer
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# import spacy
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
#import en_core_web_md

# # Initialize SpaCy model
#nlp = spacy.load("en_core_web_md")


porter = PorterStemmer()


stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text,train=True):
    if train:
        # Remove the first line
        _, *lines = text.split('\n')
        text = '\n'.join(lines)
    
    print("Text is not a string:", text)
    # Remove words between square brackets
    text = re.sub(r'\[.*?\]', '', text)
    # Convert text to lowercase
    text = text.lower()
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Handle contractions
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'s", " is", text)
    # Remove punctuations
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenization
    tokens = word_tokenize(text)
    # Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatization
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Remove tokens with less than 3 characters
    #tokens = [token for token in tokens if len(token) > 2]
    # Return unique tokens
    unique_tokens = list(set(tokens))
    preprocessed_text=" ".join(unique_tokens)
    return unique_tokens, preprocessed_text
    



# Assuming 'preprocessing' is a module you have that contains the 'preprocess' function
# If 'preprocess' is a function within the same script, you can import it directly



#commenting the path as we are not deploying lyrics in prod env 
path ="" #"web/backend/preprocessing/lyrics" # Adjust this path to the correct directory containing your documents


documents = []
documents_id=[]
# Iterate through each file in the specified directory
if path!="":
    for filename in os.listdir(path):
        doc_id = int(filename.split(".")[0])
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):  # Check if it's a file
            with open(file_path, 'r', encoding='utf-8') as f:  # Ensure correct handling of file encoding
                document = f.read()
                documents_id.append(doc_id)
                documents.append(document)

def save_bm25_model(filepath='bm25.pkl'):
    tokenized_corpus = [preprocess(doc)[0] for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)
    # Save the BM25 model to the specified filepath
    with open(filepath, 'wb') as file:
        pickle.dump(bm25, file)

    with open("doc_ids.pkl", 'wb') as file:
            pickle.dump(documents_id, file)

# def generating_spacy_and_tfidf_tokens():
#     # Compute TF-IDF vectors
#     preprocessed_corpus = [preprocess(doc)[1] for doc in documents]
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(preprocessed_corpus)

#     # Compute SpaCy vectors
#     document_vectors = [nlp(doc).vector for doc in preprocessed_corpus]
    
#     import pickle
#     with open("tfidf_embeddings.pkl", 'wb') as file:
#             pickle.dump(tfidf_matrix, file)

#     with open("tfidf_vect.pkl", 'wb') as file:
#             pickle.dump(vectorizer, file)

#     with open("spacy_embeddings.pkl", 'wb') as file:
#             pickle.dump(document_vectors, file)
    
#     with open("doc_ids.pkl", 'wb') as file:
#             pickle.dump(documents_id, file)

if __name__ == "__main__":
    # Call the function to save the BM25 model
    save_bm25_model()
    #generating_spacy_and_tfidf_tokens()            
