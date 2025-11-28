
import inspect
from youtube_transcript_api import YouTubeTranscriptApi

print("YouTubeTranscriptApi methods:")
for name, data in inspect.getmembers(YouTubeTranscriptApi):
    if inspect.isfunction(data) or inspect.ismethod(data):
        print(f"{name}: {inspect.signature(data)}")

print("\nYouTubeTranscriptApi.list_transcripts signature:")
try:
    print(inspect.signature(YouTubeTranscriptApi.list_transcripts))
except AttributeError:
    print("list_transcripts not found")
