import os
from src.youtube_client import YouTubeClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    print("YOUTUBE_API_KEY not found in environment")
    exit(1)

client = YouTubeClient(api_key, "cookies.txt")
video_id = "dQw4w9WgXcQ" # Rick Astley

print(f"Attempting to fetch transcript for {video_id} using YouTubeClient...")
transcript = client.get_transcript(video_id)

if transcript:
    print("Success! Transcript fetched.")
    print(transcript[:100] + "...")
else:
    print("Failed to fetch transcript.")
