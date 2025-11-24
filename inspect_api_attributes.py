from youtube_transcript_api import YouTubeTranscriptApi
print(f"Version: {YouTubeTranscriptApi.__module__}")
print(dir(YouTubeTranscriptApi))
try:
    import pkg_resources
    print(f"Installed version: {pkg_resources.get_distribution('youtube-transcript-api').version}")
except:
    pass
