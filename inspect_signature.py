from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("Inspecting YouTubeTranscriptApi.fetch:")
try:
    print(inspect.signature(YouTubeTranscriptApi.fetch))
    print(YouTubeTranscriptApi.fetch.__doc__)
except Exception as e:
    print(e)

print("\nInspecting YouTubeTranscriptApi.list:")
try:
    print(inspect.signature(YouTubeTranscriptApi.list))
    print(YouTubeTranscriptApi.list.__doc__)
except Exception as e:
    print(e)
