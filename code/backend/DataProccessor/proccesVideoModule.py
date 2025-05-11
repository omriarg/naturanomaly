import os
import pickle
from .main import *
from django.conf import settings
BASE_DIR=os.path.join(settings.BASE_DIR,'DataProccessor')
PROCESSED_URLS_FILE = os.path.join(BASE_DIR,'processed_urls.pkl')
def save_processed_urls(processed_urls):
    """
    Saves the list of processed URLs to the pickle file.
    """
    with open(PROCESSED_URLS_FILE, 'wb') as f:
        pickle.dump(processed_urls, f)

def load_processed_urls():
    """
    Loads the list of processed URLs from the pickle file.
    """
    if os.path.exists(PROCESSED_URLS_FILE):
        with open(PROCESSED_URLS_FILE, 'rb') as f:
            return pickle.load(f)
    return []
def process_video(video_url):
    processed_urls = load_processed_urls()
    processed_video_folder = os.path.join(BASE_DIR,'processed_video', f'Video{len(processed_urls) + 1}')

    if video_url not in processed_urls:
        if not os.path.exists(processed_video_folder):
            os.makedirs(processed_video_folder)
        try:
            # Attempt to run the main function which uses gdown to download the video
            main(video_url, processed_video_folder)
            processed_urls.append(video_url)
            save_processed_urls(processed_urls)
            return {'csv_path':os.path.join(processed_video_folder,f'Video{len(processed_urls)}','tracked_objects.csv'),'video_id':len(processed_urls),'url':video_url}
        except Exception as e:
            # If there is an error with downloading, catch the exception
            return f"{str(e)}. Make sure the URL is a valid Google Drive URL and the permissions are set to public."
    else:
        return "Video has been processed already."
process_video('https://drive.google.com/uc?id=1X6QN3wLnglkqTOL-bbVVWvq1RKsTIXY0')