import os
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

class YouTubeClient:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def _parse_duration(self, duration_iso):
        """
        Parses ISO 8601 duration (e.g., PT1H2M10S) to a readable string (e.g., 1:02:10).
        Returns a tuple: (formatted_string, total_seconds)
        """
        import re
        match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_iso)
        if not match:
            return "00:00", 0
        
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        if hours > 0:
            formatted = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            formatted = f"{minutes}:{seconds:02}"
        
        return formatted, total_seconds

    def get_videos_from_channels(self, channel_ids):
        """
        Fetches videos uploaded in the last 24 hours from the specified channels.
        """
        videos = []
        # 24 hours ago in RFC 3339 format
        published_after = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        for channel_id in channel_ids:
            try:
                # Get channel uploads playlist ID
                channel_response = self.youtube.channels().list(
                    id=channel_id,
                    part='contentDetails'
                ).execute()

                if not channel_response['items']:
                    print(f"Channel not found: {channel_id}")
                    continue

                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                # Get recent videos from the uploads playlist
                playlist_response = self.youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='snippet',
                    maxResults=10
                ).execute()

                for item in playlist_response.get('items', []):
                    snippet = item['snippet']
                    published_at = snippet['publishedAt']
                    
                    if published_at > published_after:
                        video_id = snippet['resourceId']['videoId']
                        
                        # Fetch additional details (duration, view count)
                        video_details = self.youtube.videos().list(
                            id=video_id,
                            part='contentDetails,statistics'
                        ).execute()
                        
                        if not video_details['items']:
                            continue
                            
                        details = video_details['items'][0]
                        duration, duration_seconds = self._parse_duration(details['contentDetails']['duration'])
                        
                        # ショート動画（60秒以下）を除外
                        if duration_seconds <= 60:
                            print(f"Skipping short video (duration: {duration}): {snippet['title']}")
                            continue
                        
                        view_count = details['statistics'].get('viewCount', '0')
                        thumbnail = snippet['thumbnails'].get('high', snippet['thumbnails']['default'])['url']

                        videos.append({
                            'video_id': video_id,
                            'title': snippet['title'],
                            'channel_title': snippet['channelTitle'],
                            'published_at': published_at,
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'duration': duration,
                            'view_count': int(view_count),
                            'thumbnail': thumbnail
                        })
            except Exception as e:
                print(f"Error fetching videos for channel {channel_id}: {e}")

        return videos

    def get_transcript(self, video_id):
        """
        Fetches the transcript for a given video ID using youtube-transcript-api v1.2.3.
        Attempts to get Japanese or English transcript.
        """
        try:
            # Initialize the API client
            ytt_api = YouTubeTranscriptApi()
            
            # fetch() method accepts a languages parameter as a priority list
            # It will try languages in order: Japanese first, then English
            fetched_transcript = ytt_api.fetch(video_id, languages=['ja', 'en'])
            
            # Convert FetchedTranscript object to raw data (list of dicts)
            raw_data = fetched_transcript.to_raw_data()
            
            # Combine all text entries into a single string
            full_text = " ".join([entry['text'] for entry in raw_data])
            return full_text

        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {e}")
            return None
