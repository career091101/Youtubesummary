"""
Webshare Proxy Manager for YouTube Transcript API

This module provides proxy rotation functionality to avoid IP restrictions
when fetching YouTube transcripts using the unofficial API.
"""

import os
import time
import random
import requests
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ProxyInfo:
    """Represents a single proxy with its statistics."""
    host: str
    port: int
    username: str
    password: str
    failure_count: int = 0
    success_count: int = 0
    last_used: Optional[datetime] = None
    disabled_until: Optional[datetime] = None
    
    @property
    def url(self) -> str:
        """Returns the proxy URL in the format http://user:pass@host:port"""
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"
    
    @property
    def as_dict(self) -> Dict[str, str]:
        """Returns proxy configuration for requests library."""
        proxy_url = self.url
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def is_available(self) -> bool:
        """Check if the proxy is currently available."""
        if self.disabled_until is None:
            return True
        return datetime.now() > self.disabled_until


class ProxyManager:
    """
    Manages a list of proxies with rotation and failure handling.
    
    Features:
    - Load proxies from file or Webshare API
    - Round-robin proxy rotation
    - Automatic failure tracking and temporary disabling
    - Statistics logging
    """
    
    # Webshare API endpoint for proxy list
    WEBSHARE_API_URL = "https://proxy.webshare.io/api/v2/proxy/list/"
    WEBSHARE_DOWNLOAD_URL = "https://proxy.webshare.io/api/v2/proxy/list/download/{token}/"
    
    def __init__(
        self,
        proxy_file: Optional[str] = None,
        webshare_token: Optional[str] = None,
        failure_threshold: int = 3,
        disable_duration_minutes: int = 30,
        shuffle: bool = True
    ):
        """
        Initialize the proxy manager.
        
        Args:
            proxy_file: Path to proxy list file (format: ip:port:username:password)
            webshare_token: Webshare API token for fetching proxy list
            failure_threshold: Number of failures before temporarily disabling a proxy
            disable_duration_minutes: Duration to disable a failed proxy
            shuffle: Whether to shuffle the proxy list on load
        """
        self.proxy_file = proxy_file
        self.webshare_token = webshare_token
        self.failure_threshold = failure_threshold
        self.disable_duration = timedelta(minutes=disable_duration_minutes)
        self.shuffle = shuffle
        
        self.proxies: List[ProxyInfo] = []
        self.current_index: int = 0
        
        # Load proxies
        self._load_proxies()
        
        if self.proxies:
            logger.info(f"ProxyManager initialized with {len(self.proxies)} proxies")
        else:
            logger.warning("ProxyManager initialized with no proxies - will operate without proxy")
    
    def _load_proxies(self) -> None:
        """Load proxies from file or Webshare API."""
        # Try loading from file first
        if self.proxy_file and os.path.exists(self.proxy_file):
            self._load_from_file()
        # Try Webshare API if token is provided and file loading failed
        elif self.webshare_token:
            self._load_from_webshare_api()
        
        # Shuffle if requested
        if self.shuffle and self.proxies:
            random.shuffle(self.proxies)
            logger.debug("Proxy list shuffled")
    
    def _load_from_file(self) -> None:
        """Load proxies from a file."""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                proxy = self._parse_proxy_line(line)
                if proxy:
                    self.proxies.append(proxy)
            
            logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            
        except Exception as e:
            logger.error(f"Failed to load proxies from file: {e}")
    
    def _parse_proxy_line(self, line: str) -> Optional[ProxyInfo]:
        """
        Parse a proxy line in the format: ip:port:username:password
        Also supports: ip:port (for unauthenticated proxies)
        """
        parts = line.split(':')
        
        if len(parts) == 4:
            # Authenticated proxy: ip:port:username:password
            host, port, username, password = parts
            try:
                return ProxyInfo(
                    host=host.strip(),
                    port=int(port.strip()),
                    username=username.strip(),
                    password=password.strip()
                )
            except ValueError as e:
                logger.warning(f"Invalid proxy format: {line} - {e}")
                return None
        elif len(parts) == 2:
            # Unauthenticated proxy: ip:port
            host, port = parts
            try:
                return ProxyInfo(
                    host=host.strip(),
                    port=int(port.strip()),
                    username='',
                    password=''
                )
            except ValueError as e:
                logger.warning(f"Invalid proxy format: {line} - {e}")
                return None
        else:
            logger.warning(f"Invalid proxy format: {line}")
            return None
    
    def _load_from_webshare_api(self) -> None:
        """Load proxies from Webshare API."""
        try:
            headers = {
                'Authorization': f'Token {self.webshare_token}'
            }
            
            response = requests.get(
                self.WEBSHARE_API_URL,
                headers=headers,
                params={'mode': 'direct', 'page_size': 100}
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            for proxy_data in results:
                proxy = ProxyInfo(
                    host=proxy_data.get('proxy_address', ''),
                    port=int(proxy_data.get('port', 0)),
                    username=proxy_data.get('username', ''),
                    password=proxy_data.get('password', '')
                )
                if proxy.host and proxy.port:
                    self.proxies.append(proxy)
            
            logger.info(f"Loaded {len(self.proxies)} proxies from Webshare API")
            
        except requests.RequestException as e:
            logger.error(f"Failed to load proxies from Webshare API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading from Webshare API: {e}")
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the next available proxy using round-robin rotation.
        
        Returns:
            Proxy configuration dict for requests library, or None if no proxies available
        """
        if not self.proxies:
            return None
        
        # Try to find an available proxy
        attempts = 0
        max_attempts = len(self.proxies)
        
        while attempts < max_attempts:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy.is_available():
                proxy.last_used = datetime.now()
                logger.debug(f"Using proxy: {proxy.host}:{proxy.port}")
                return proxy.as_dict
            
            attempts += 1
        
        # All proxies are temporarily disabled, use the least recently failed one
        logger.warning("All proxies temporarily disabled, using least recently failed")
        available_proxies = sorted(
            self.proxies,
            key=lambda p: p.disabled_until or datetime.min
        )
        proxy = available_proxies[0]
        proxy.last_used = datetime.now()
        return proxy.as_dict
    
    def mark_proxy_success(self, proxy_dict: Dict[str, str]) -> None:
        """Mark a proxy as successfully used."""
        proxy = self._find_proxy_by_dict(proxy_dict)
        if proxy:
            proxy.success_count += 1
            proxy.failure_count = 0  # Reset failure count on success
            logger.debug(f"Proxy success: {proxy.host}:{proxy.port} (total: {proxy.success_count})")
    
    def mark_proxy_failed(self, proxy_dict: Dict[str, str]) -> None:
        """
        Mark a proxy as failed. If failure threshold is reached,
        temporarily disable the proxy.
        """
        proxy = self._find_proxy_by_dict(proxy_dict)
        if proxy:
            proxy.failure_count += 1
            
            if proxy.failure_count >= self.failure_threshold:
                proxy.disabled_until = datetime.now() + self.disable_duration
                logger.warning(
                    f"Proxy disabled: {proxy.host}:{proxy.port} "
                    f"(failures: {proxy.failure_count}, disabled until: {proxy.disabled_until})"
                )
            else:
                logger.debug(
                    f"Proxy failure: {proxy.host}:{proxy.port} "
                    f"(failures: {proxy.failure_count}/{self.failure_threshold})"
                )
    
    def _find_proxy_by_dict(self, proxy_dict: Dict[str, str]) -> Optional[ProxyInfo]:
        """Find a ProxyInfo object by its dict representation."""
        if not proxy_dict:
            return None
        
        proxy_url = proxy_dict.get('http', '') or proxy_dict.get('https', '')
        
        for proxy in self.proxies:
            if proxy.url in proxy_url or f"{proxy.host}:{proxy.port}" in proxy_url:
                return proxy
        
        return None
    
    def get_stats(self) -> Dict:
        """Get statistics about the proxy pool."""
        if not self.proxies:
            return {
                'total': 0,
                'available': 0,
                'disabled': 0,
                'total_successes': 0,
                'total_failures': 0
            }
        
        available = sum(1 for p in self.proxies if p.is_available())
        disabled = len(self.proxies) - available
        total_successes = sum(p.success_count for p in self.proxies)
        total_failures = sum(p.failure_count for p in self.proxies)
        
        return {
            'total': len(self.proxies),
            'available': available,
            'disabled': disabled,
            'total_successes': total_successes,
            'total_failures': total_failures
        }
    
    def log_stats(self) -> None:
        """Log current proxy pool statistics."""
        stats = self.get_stats()
        logger.info(
            f"Proxy stats - Total: {stats['total']}, "
            f"Available: {stats['available']}, "
            f"Disabled: {stats['disabled']}, "
            f"Successes: {stats['total_successes']}, "
            f"Failures: {stats['total_failures']}"
        )
    
    def reset_all(self) -> None:
        """Reset all proxy statistics and re-enable all proxies."""
        for proxy in self.proxies:
            proxy.failure_count = 0
            proxy.success_count = 0
            proxy.disabled_until = None
        logger.info("All proxy statistics reset")
    
    def has_proxies(self) -> bool:
        """Check if any proxies are loaded."""
        return len(self.proxies) > 0
