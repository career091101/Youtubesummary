import os
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple, Any
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import ProxyConfig
from .logger import setup_logger
from .transcript_cache import TranscriptCache
from .exceptions import IPBlockingError, RateLimitError, TranscriptError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .proxy_manager import ProxyManager


class RotatingProxyConfig(ProxyConfig):
    """
    Custom ProxyConfig implementation for rotating proxies.
    This integrates with our ProxyManager to provide proper proxy rotation.
    """
    
    def __init__(self, proxy_dict: Dict[str, str], retries: int = 3):
        """
        Initialize with a proxy dictionary from ProxyManager.
        
        Args:
            proxy_dict: Proxy configuration dict with 'http' and 'https' keys
            retries: Number of retries when blocked
        """
        self._proxy_dict = proxy_dict
        self._retries = retries
    
    def to_requests_dict(self) -> Dict[str, str]:
        """Return the proxy dict for requests library."""
        return self._proxy_dict
    
    @property
    def prevent_keeping_connections_alive(self) -> bool:
        """Prevent keeping connections alive for proper rotation."""
        return True
    
    @property
    def retries_when_blocked(self) -> int:
        """Number of retries when blocked."""
        return self._retries

logger = setup_logger(__name__)


class YouTubeClient:
    def __init__(self, api_key: str, cookies_file: Optional[str] = None, 
                 cache_dir: Optional[str] = None, cache_expiry_days: int = 7,
                 max_retries: int = 3, backoff_factor: int = 2,
                 proxy_manager: Optional['ProxyManager'] = None,
                 user_agent: Optional[str] = None):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.cookies_file = cookies_file
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.proxy_manager = proxy_manager
        self.user_agent = user_agent
        
        # Initialize transcript cache
        if cache_dir:
            self.cache = TranscriptCache(cache_dir, cache_expiry_days)
            logger.info(f"Transcript cache enabled: {cache_dir}")
        else:
            self.cache = None
            logger.info("Transcript cache disabled")
        
        # Log proxy configuration
        if proxy_manager and proxy_manager.has_proxies():
            logger.info(f"Proxy rotation enabled with {len(proxy_manager.proxies)} proxies")
        else:
            logger.info("No proxy rotation configured")
        
        # Log User-Agent configuration
        if user_agent:
            logger.info(f"Custom User-Agent configured: {user_agent[:50]}...")
        else:
            logger.info("Using default User-Agent")

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
        Fetches videos uploaded in the last N days from the specified channels.
        """
        from .config import Config
        
        videos = []
        # N days ago in RFC 3339 format
        published_after = (datetime.now(timezone.utc) - timedelta(days=Config.DAYS_TO_FETCH)).isoformat()

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
                        
                        # 短い動画を除外
                        if duration_seconds <= Config.MIN_VIDEO_DURATION_SECONDS:
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
                logger.info(f"Using cached transcript for video {video_id}")
                return cached_transcript
        
        # Try to fetch transcript with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Try to get transcript list using correct API method
                logger.info(f"Fetching transcript for video {video_id} (attempt {attempt + 1}/{self.max_retries})")
                
                # Get proxy from rotation if available
                current_proxy = None
                proxy_config = None
                
                if self.proxy_manager and self.proxy_manager.has_proxies():
                    current_proxy = self.proxy_manager.get_next_proxy()
                    if current_proxy:
                        # Create ProxyConfig for properly rotating proxies
                        proxy_config = RotatingProxyConfig(current_proxy, retries=0)
                        logger.debug(f"Using rotating proxy for video {video_id}")
                
                # Prepare HTTP client with cookies if available
                http_client = None
                if self.cookies_file and os.path.exists(self.cookies_file):
                    try:
                        import requests
                        from http.cookiejar import MozillaCookieJar
                        http_client = requests.Session()
                        http_client.cookies = MozillaCookieJar(self.cookies_file)
                        http_client.cookies.load(ignore_discard=True, ignore_expires=True)
                        logger.debug(f"Loaded cookies from {self.cookies_file}")
                    except Exception as e:
                        logger.warning(f"Failed to load cookies: {e}")
                        http_client = None

                # Initialize API with proxy config
                api = YouTubeTranscriptApi(
                    proxy_config=proxy_config,
                    http_client=http_client
                )
                
                transcript_list = api.list(video_id)

                
                # Try to find Japanese transcript first, then English
                transcript = None
                try:
                    transcript = transcript_list.find_transcript(['ja'])
                    logger.debug(f"Found Japanese transcript for video {video_id}")
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                        logger.debug(f"Found English transcript for video {video_id}")
                    except:
                        # Get any available transcript
                        transcript = transcript_list.find_generated_transcript(['ja', 'en'])
                        logger.debug(f"Using generated transcript for video {video_id}")
                
                # Fetch the transcript data
                fetched_transcript = transcript.fetch()
                
                # Combine all text entries into a single string
                try:
                    full_text = " ".join([entry['text'] for entry in fetched_transcript])
                except TypeError:
                    # Fallback for object access if dict access fails
                    logger.debug("Using attribute access for transcript entries")
                    full_text = " ".join([entry.text for entry in fetched_transcript])
                
                # Cache the result
                if self.cache:
                    self.cache.set(video_id, full_text)
                
                # Mark proxy as successful
                if self.proxy_manager and current_proxy:
                    self.proxy_manager.mark_proxy_success(current_proxy)
                
                logger.info(f"Successfully fetched transcript for video {video_id} ({len(full_text)} chars)")
                return full_text
                
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.warning(f"No transcript available for video {video_id}: {e}")
                return None
                
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                
                # Extract HTTP status code if available
                http_status = None
                if hasattr(e, 'status_code'):
                    http_status = e.status_code
                elif '429' in error_msg or 'Too Many Requests' in error_msg:
                    http_status = 429
                elif '403' in error_msg or 'Forbidden' in error_msg:
                    http_status = 403
                
                # Log detailed error information
                logger.warning(
                    f"Error fetching transcript for video {video_id}. "
                    f"Type: {error_type}, HTTP Status: {http_status or 'N/A'}, "
                    f"Message: {error_msg}"
                )
                
                # Check if it's an IP blocking error
                if "blocking" in error_msg.lower() or "cloud provider" in error_msg.lower() or http_status == 403:
                    logger.error(
                        f"YouTube is blocking requests from this IP address for video {video_id}. "
                        f"This is a known issue when running from cloud providers. "
                        f"Consider using a proxy or VPN. Error: {error_msg}"
                    )
                    # Mark proxy as failed
                    if self.proxy_manager and current_proxy:
                        self.proxy_manager.mark_proxy_failed(current_proxy)
                    # IP制限エラーはこのプロキシでは無駄なので次のプロキシで再試行
                    if self.proxy_manager and self.proxy_manager.has_proxies() and attempt < self.max_retries - 1:
                        logger.info("Trying next proxy...")
                        continue
                    return None
                
                # Special handling for 429 (rate limit) errors
                if http_status == 429:
                    # Mark proxy as failed for rate limiting
                    if self.proxy_manager and current_proxy:
                        self.proxy_manager.mark_proxy_failed(current_proxy)
                    
                    if attempt < self.max_retries - 1:
                        wait_time = 60  # Wait 60 seconds for rate limit errors
                        logger.warning(
                            f"Rate limit (429) detected for video {video_id}. "
                            f"Waiting {wait_time} seconds before retry (attempt {attempt + 1}/{self.max_retries})..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Rate limit exceeded for video {video_id} after {self.max_retries} attempts")
                        return None
                # Handle other errors with exponential backoff (starting at 5 seconds)
                elif attempt < self.max_retries - 1:
                    wait_time = 5 * (self.backoff_factor ** attempt)  # Start at 5 seconds
                    logger.warning(
                        f"Retrying video {video_id} in {wait_time} seconds "
                        f"(attempt {attempt + 1}/{self.max_retries})..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to fetch transcript for video {video_id} after {self.max_retries} attempts. "
                        f"Last error: {error_type} - {error_msg}"
                    )
                    return None
        
        return None


