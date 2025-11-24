from src.youtube_client import YouTubeClient
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env for API key (though transcript api doesn't strictly need it, the client init does)
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY', 'DUMMY_KEY')

cookies_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')
cache_dir = os.path.join(os.path.dirname(__file__), '.cache')

# Initialize client with caching and retry logic
client = YouTubeClient(
    api_key, 
    cookies_file,
    cache_dir=cache_dir,
    cache_expiry_days=7,
    max_retries=3,
    backoff_factor=2
)

# Known video with Japanese subtitles (or English)
# Example: "Python in 100 Seconds" (English) or a random Japanese tech video
# Let's use a stable one. "Python in 100 Seconds" ID: x7X9w_GIm1s
VIDEO_ID = "x7X9w_GIm1s" 

print(f"Attempting to fetch transcript for video: {VIDEO_ID}")
transcript = client.get_transcript(VIDEO_ID)

if transcript:
    print("\n--- SUCCESS: Transcript Retrieved ---")
    print(f"Length: {len(transcript)} characters")
    print(f"Preview: {transcript[:100]}...")
else:
    print("\n--- FAILED: Could not retrieve transcript ---")
