import os
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple, Any
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from .logger import setup_logger
from .transcript_cache import TranscriptCache

logger = setup_logger(__name__)

class YouTubeClient:
    def __init__(self, api_key: str, cookies_file: Optional[str] = None, 
                 cache_dir: Optional[str] = None, cache_expiry_days: int = 7,
                 max_retries: int = 3, backoff_factor: int = 2,
                 proxies: Optional[Dict[str, str]] = None):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.cookies_file = cookies_file
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.proxies = proxies
        
        # Initialize transcript cache
        if cache_dir:
            self.cache = TranscriptCache(cache_dir, cache_expiry_days)
            logger.info(f"Transcript cache enabled: {cache_dir}")
        else:
            self.cache = None
            logger.info("Transcript cache disabled")
        
        # Log proxy configuration
        if proxies:
            logger.info(f"Proxy enabled: {proxies}")
        else:
            logger.info("No proxy configured")

    def _parse_duration(self, duration_iso: str) -> Tuple[str, int]:
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

    def get_videos_from_channels(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
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
                    logger.warning(f"Channel not found: {channel_id}")
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
                            logger.info(f"Skipping short video (duration: {duration}): {snippet['title']}")
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
                logger.error(f"Error fetching videos for channel {channel_id}: {e}")

        return videos

    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Fetches the transcript for a given video ID using youtube-transcript-api.
        Implements caching and exponential backoff retry logic to avoid IP restrictions.
        Attempts to get Japanese or English transcript.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None if not available
        """
        # Check cache first
        if self.cache:
            cached_transcript = self.cache.get(video_id)
            if cached_transcript:
                return cached_transcript
        
        # Try to fetch transcript with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Initialize the API client
                cookies = None
                if self.cookies_file and os.path.exists(self.cookies_file):
                    cookies = self.cookies_file

                # Create API instance
                api = YouTubeTranscriptApi()
                
                # Try to get transcript in Japanese or English
                try:
                    fetched_transcript = api.fetch(video_id, ['ja', 'en'])
                except:
                    # If specific language fails, try with default (English)
                    fetched_transcript = api.fetch(video_id)

                
                # Combine all text entries into a single string
                full_text = " ".join([entry.text for entry in fetched_transcript])
                
                # Cache the result
                if self.cache:
                    self.cache.set(video_id, full_text)
                
                logger.info(f"Successfully fetched transcript for video {video_id}")
                return full_text

                
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.warning(f"No transcript found for video {video_id}: {e}")
                return None
                
            except Exception as e:
                # Handle other errors with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    logger.warning(
                        f"Error fetching transcript for video {video_id}. "
                        f"Attempt {attempt + 1}/{self.max_retries}. "
                        f"Waiting {wait_time} seconds before retry... Error: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch transcript for video {video_id} after {self.max_retries} attempts: {e}")
                    return None
        
        return None

