from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("Inspecting YouTubeTranscriptApi.__init__:")
try:
    print(inspect.signature(YouTubeTranscriptApi.__init__))
    print(YouTubeTranscriptApi.__init__.__doc__)
except Exception as e:
    print(e)
