from youtube_transcript_api import YouTubeTranscriptApi
import os

# Use a video that is likely to be available. 
# "dQw4w9WgXcQ" is Rick Astley - Never Gonna Give You Up.
video_id = "dQw4w9WgXcQ" 

cookies_file = "cookies.txt"
if not os.path.exists(cookies_file):
    print(f"Error: {cookies_file} not found in current directory.")
    exit(1)

print(f"Found {cookies_file}.")

try:
    print(f"Attempting to fetch transcript for video ID: {video_id} using cookies...")
    # The cookies parameter expects a path to the Netscape cookie file
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_file)
    
    print("Success! Transcript list retrieved.")
    
    # Try to fetch the actual transcript to be sure
    transcript = transcript_list.find_transcript(['en', 'ja'])
    fetched_transcript = transcript.fetch()
    
    print(f"Successfully fetched {len(fetched_transcript)} lines of transcript.")
    print("First line:", fetched_transcript[0])
    
except Exception as e:
    print(f"Failed to fetch transcript: {e}")
    exit(1)
