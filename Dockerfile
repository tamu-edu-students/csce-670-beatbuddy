# Use a base image
FROM python:3.9-slim

# Install build tools and nltk
# RUN apt-get update && apt-get install -y gcc python3-dev \
#     && pip install nltk

RUN apt-get update --fix-missing 
RUN apt-get install -y gcc python3-dev 
RUN pip install nltk

# Set the working directory inside the container
WORKDIR /app

# Copy application files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Download NLTK resources
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader wordnet

EXPOSE 8000
# Specify the command to run when the container starts
CMD ["python3", "app.py"]
