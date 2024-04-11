import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import yt_dlp as youtube_dl
import os
import logging

# Setup logging
logging.basicConfig(filename='download_log.txt', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def search_youtube(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    search_url = f"https://www.youtube.com/results?search_query={search_query}"
    driver.get(search_url)

    video_url = None
    try:
        wait = WebDriverWait(driver, 10)
        video = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer,#items > ytd-video-renderer")))
        video_url = video.find_element(By.ID, "video-title").get_attribute('href')
        logging.info(f"Successfully found YouTube URL for {search_query}: {video_url}")
    except Exception as e:
        logging.error(f"Failed to find video for: {search_query}. Error: {e}")
    finally:
        driver.quit()
    return video_url

def download_video_as_mp3(url, save_path, filename):
    # Check if the file already exists
    output_file_path = os.path.join(save_path, f"{filename}.mp3")
    if os.path.exists(output_file_path):
        logging.info(f"File '{filename}.mp3' already exists, skipping download.")
        return  # Exit the function early
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'external-downloader': 'aria2c',
        'external-downloader-args': '-x16 -s16 -k1M',
        'outtmpl': output_file_path,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logging.info(f"Successfully downloaded: {filename}.mp3")
    except Exception as e:
        logging.error(f"Failed to download {url}. Error: {e}")

def search_and_download(df, author_song_df, save_path='./mp3s', csv_path='updated_dataset_with_youtube_urls.csv'):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    for _, row in df.iterrows():
        search_query = f"{row['artists']} {row['track_name']} official music video"
        logging.info(f"Searching for: {search_query}")
        
        youtube_url = search_youtube(search_query)  # Function to search YouTube
        if youtube_url:
            # Update the YouTube URL for the matching row based on 'track_name' and 'artists'
            author_song_df.loc[(author_song_df['track_name'] == row['track_name']) & (author_song_df['artists'] == row['artists']), 'YouTube URL'] = youtube_url
            filename = f"{row['track_name']} - {row['artists']}"
            download_video_as_mp3(youtube_url, save_path, filename)  # Function to download the video as MP3
            author_song_df.to_csv(csv_path, index=False)
    
    logging.info("Updated dataset saved.")


if __name__ == "__main__":
    dataset_path = "dataset.csv"
    df = pd.read_csv(dataset_path)
    author_song_df = pd.read_csv('updated_dataset_with_youtube_urls.csv')
    df = df[1198:5000]
    search_and_download(df, author_song_df)


