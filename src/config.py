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
    
    # Webshare Proxy Settings (for IP rotation)
    WEBSHARE_API_TOKEN = os.getenv('WEBSHARE_API_TOKEN')  # Optional: for API-based proxy list
    PROXY_LIST_FILE = os.path.join(BASE_DIR, 'proxy_list.txt')  # Proxy list file path
    PROXY_ROTATION_ENABLED = os.getenv('PROXY_ROTATION_ENABLED', 'true').lower() == 'true'
    PROXY_FAILURE_THRESHOLD = int(os.getenv('PROXY_FAILURE_THRESHOLD', '3'))  # Max failures before disable
    PROXY_DISABLE_DURATION = int(os.getenv('PROXY_DISABLE_DURATION', '30'))  # Minutes to disable failed proxy
    
    # App Settings
    MAX_VIDEOS = int(os.getenv('MAX_VIDEOS', 20))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 20))  # seconds - delay between video processing to avoid IP blocking
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))  # maximum number of retry attempts for failed requests
    BACKOFF_FACTOR = int(os.getenv('BACKOFF_FACTOR', 3))  # exponential backoff multiplier for retries
    CACHE_DIR = os.path.join(BASE_DIR, '.cache')
    CACHE_EXPIRY_DAYS = 7  # transcript cache expiry in days
    PROCESSED_VIDEOS_FILE = os.path.join(BASE_DIR, 'processed_videos.txt')
    
    # Video Filtering Constants
    MIN_VIDEO_DURATION_SECONDS = 300  # 5分
    DAYS_TO_FETCH = 3  # 直近3日間の動画を取得
    
    # Email Templates
    EMAIL_SUBJECT_TEMPLATE = "【YouTube要約】{count}本の新着動画があります"
    EMAIL_NO_UPDATES_SUBJECT = "【YouTube要約】新着動画はありませんでした"
    EMAIL_NO_UPDATES_BODY = "直近の更新はありませんでした。"
    
    # User-Agent for avoiding bot detection
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


    
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
