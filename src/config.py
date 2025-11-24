import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Gmail Settings
    GMAIL_USER = os.getenv('GMAIL_USER')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CHANNEL_IDS_FILE = os.path.join(BASE_DIR, 'channel_ids.txt')
    COOKIES_FILE = os.path.join(BASE_DIR, 'cookies.txt')
    
    # Proxy Settings (optional - for avoiding IP restrictions)
    PROXY_HTTP = os.getenv('PROXY_HTTP')  # e.g., 'http://proxy.example.com:8080'
    PROXY_HTTPS = os.getenv('PROXY_HTTPS')  # e.g., 'https://proxy.example.com:8080'
    
    # App Settings
    MAX_VIDEOS = 50
    RETRY_DELAY = 5  # seconds - delay between video processing to avoid IP blocking
    MAX_RETRIES = 3  # maximum number of retry attempts for failed requests
    BACKOFF_FACTOR = 2  # exponential backoff multiplier for retries
    CACHE_DIR = os.path.join(BASE_DIR, '.cache')
    CACHE_EXPIRY_DAYS = 7  # transcript cache expiry in days
    PROCESSED_VIDEOS_FILE = os.path.join(BASE_DIR, 'processed_videos.txt')


    
    @classmethod
    def get_channel_ids(cls):
        channel_ids = []
        if os.path.exists(cls.CHANNEL_IDS_FILE):
            with open(cls.CHANNEL_IDS_FILE, 'r', encoding='utf-8') as f:
                channel_ids = [line.strip() for line in f if line.strip()]
        
        if not channel_ids:
            env_ids = os.getenv('TARGET_CHANNEL_IDS', '').split(',')
            channel_ids = [cid for cid in env_ids if cid]
            
        return channel_ids

    @classmethod
    def validate(cls):
        required_vars = [
            cls.YOUTUBE_API_KEY,
            cls.OPENAI_API_KEY,
            cls.GMAIL_USER,
            cls.GMAIL_APP_PASSWORD,
            cls.EMAIL_RECIPIENT
        ]
        if not all(required_vars):
            return False
        if not cls.get_channel_ids():
            return False
        return True
