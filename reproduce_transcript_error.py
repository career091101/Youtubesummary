
import sys
import logging
from src.youtube_client import YouTubeClient
from src.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize client
    client = YouTubeClient(
        Config.YOUTUBE_API_KEY,
        Config.COOKIES_FILE,
        cache_dir=Config.CACHE_DIR
    )

    # Test with a known video ID (or one that failed if we knew it)
    # Let's use a recent video ID if possible, or a hardcoded one.
    # This is a random recent video ID for testing.
    test_video_id = "jNQXAC9IVRw" # Me at the zoo (very old, but has transcript)
    # Or better, a recent tech video.
    # Let's try to fetch a video from a channel in the list.
    
    logger.info(f"Attempting to fetch transcript for {test_video_id}")
    transcript = client.get_transcript(test_video_id)
    
    if transcript:
        logger.info("SUCCESS: Transcript fetched.")
        print(transcript[:100] + "...")
    else:
        logger.error("FAILURE: Could not fetch transcript.")

if __name__ == "__main__":
    main()
