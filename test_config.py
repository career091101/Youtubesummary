import os
import sys
from src.config import Config

def test_config():
    print("Testing Config module...")
    
    # Check if environment variables are loaded
    print(f"YOUTUBE_API_KEY present: {bool(Config.YOUTUBE_API_KEY)}")
    print(f"OPENAI_API_KEY present: {bool(Config.OPENAI_API_KEY)}")
    print(f"GMAIL_USER present: {bool(Config.GMAIL_USER)}")
    
    # Check channel IDs
    channel_ids = Config.get_channel_ids()
    print(f"Channel IDs loaded: {len(channel_ids)}")
    if channel_ids:
        print(f"First channel ID: {channel_ids[0]}")
    
    # Validate
    is_valid = Config.validate()
    print(f"Config validation: {'✅ Passed' if is_valid else '❌ Failed'}")
    
    if not is_valid:
        print("Validation failed. Missing variables:")
        if not Config.YOUTUBE_API_KEY: print("- YOUTUBE_API_KEY")
        if not Config.OPENAI_API_KEY: print("- OPENAI_API_KEY")
        if not Config.GMAIL_USER: print("- GMAIL_USER")
        if not Config.GMAIL_APP_PASSWORD: print("- GMAIL_APP_PASSWORD")
        if not Config.EMAIL_RECIPIENT: print("- EMAIL_RECIPIENT")
        if not channel_ids: print("- Channel IDs")

if __name__ == "__main__":
    test_config()
