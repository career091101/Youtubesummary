import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from .logger import setup_logger

logger = setup_logger(__name__)

class TranscriptCache:
    """
    File-based cache for YouTube transcripts to reduce API requests and avoid IP restrictions.
    """
    
    def __init__(self, cache_dir: str, expiry_days: int = 7):
        """
        Initialize the transcript cache.
        
        Args:
            cache_dir: Directory to store cache files
            expiry_days: Number of days before cache entries expire
        """
        self.cache_dir = cache_dir
        self.expiry_days = expiry_days
        self.cache_file = os.path.join(cache_dir, 'transcripts.json')
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache or create new one
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file or create empty cache."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded transcript cache with {len(self.cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache file: {e}. Creating new cache.")
                self.cache = {}
        else:
            self.cache = {}
            logger.info("Created new transcript cache")
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved transcript cache with {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache file: {e}")
    
    def get(self, video_id: str) -> Optional[str]:
        """
        Get transcript from cache if it exists and hasn't expired.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Cached transcript text or None if not found or expired
        """
        if video_id not in self.cache:
            logger.debug(f"Cache miss for video {video_id}")
            return None
        
        entry = self.cache[video_id]
        cached_time = datetime.fromisoformat(entry['timestamp'])
        expiry_time = cached_time + timedelta(days=self.expiry_days)
        
        if datetime.now() > expiry_time:
            logger.info(f"Cache expired for video {video_id}")
            del self.cache[video_id]
            self._save_cache()
            return None
        
        logger.info(f"Cache hit for video {video_id}")
        return entry['transcript']
    
    def set(self, video_id: str, transcript: str):
        """
        Store transcript in cache.
        
        Args:
            video_id: YouTube video ID
            transcript: Transcript text to cache
        """
        self.cache[video_id] = {
            'transcript': transcript,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
        logger.info(f"Cached transcript for video {video_id}")
    
    def cleanup(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = []
        
        for video_id, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            expiry_time = cached_time + timedelta(days=self.expiry_days)
            
            if now > expiry_time:
                expired_keys.append(video_id)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear(self):
        """Clear all cache entries."""
        self.cache = {}
        self._save_cache()
        logger.info("Cleared all cache entries")
    
    def stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.cache)
        now = datetime.now()
        expired_count = 0
        
        for entry in self.cache.values():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            expiry_time = cached_time + timedelta(days=self.expiry_days)
            if now > expiry_time:
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'valid_entries': total_entries - expired_count,
            'expired_entries': expired_count,
            'cache_file': self.cache_file
        }
