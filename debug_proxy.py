#!/usr/bin/env python3
"""
Debug proxy usage with YouTube Transcript API
"""

import os
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig

# Custom ProxyConfig for debugging
class DebugProxyConfig(ProxyConfig):
    def __init__(self, proxy_url: str):
        self.proxy_url = proxy_url
        print(f"[DEBUG] Creating ProxyConfig with: {proxy_url}")
    
    def to_requests_dict(self):
        result = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        print(f"[DEBUG] to_requests_dict() returning: {result}")
        return result
    
    @property
    def prevent_keeping_connections_alive(self):
        print("[DEBUG] prevent_keeping_connections_alive: True")
        return True
    
    @property
    def retries_when_blocked(self):
        print("[DEBUG] retries_when_blocked: 0")
        return 0


def test_direct_proxy():
    """Test proxy directly with requests"""
    print("=" * 80)
    print("Test 1: Direct Proxy Test with requests library")
    print("=" * 80)
    
    proxy_url = "http://xngcspkb:m8igrend5ylt@23.27.208.120:5830"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    try:
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        print(f"✅ Direct proxy test successful")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Direct proxy test failed: {e}")
    
    print()


def test_youtube_api_with_proxy():
    """Test YouTube Transcript API with proxy"""
    print("=" * 80)
    print("Test 2: YouTube Transcript API with ProxyConfig")
    print("=" * 80)
    
    video_id = "dQw4w9WgXcQ"
    proxy_url = "http://xngcspkb:m8igrend5ylt@23.27.208.120:5830"
    
    print(f"Testing video: {video_id}")
    print(f"Using proxy: {proxy_url}")
    print()
    
    try:
        proxy_config = DebugProxyConfig(proxy_url)
        api = YouTubeTranscriptApi(proxy_config=proxy_config)
        
        print("[DEBUG] Calling api.list()...")
        transcript_list = api.list(video_id)
        
        print("[DEBUG] Looking for transcript...")
        transcript = transcript_list.find_transcript(['en'])
        
        print("[DEBUG] Fetching transcript...")
        data = transcript.fetch()
        
        text = " ".join([entry['text'] for entry in data[:5]])
        print(f"✅ Success! First 5 entries: {text[:100]}...")
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    
    print()


def test_youtube_api_without_proxy():
    """Test YouTube Transcript API without proxy (baseline)"""
    print("=" * 80)
    print("Test 3: YouTube Transcript API WITHOUT proxy (baseline)")
    print("=" * 80)
    
    video_id = "dQw4w9WgXcQ"
    
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(['en'])
        data = transcript.fetch()
        text = " ".join([entry['text'] for entry in data[:5]])
        print(f"✅ Success! First 5 entries: {text[:100]}...")
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    
    print()


def test_session_with_proxy():
    """Test with custom session"""
    print("=" * 80)
    print("Test 4: YouTube Transcript API with Session + Proxy")
    print("=" * 80)
    
    video_id = "dQw4w9WgXcQ"
    proxy_url = "http://xngcspkb:m8igrend5ylt@23.27.208.120:5830"
    
    try:
        session = requests.Session()
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        # Test session first
        print("[DEBUG] Testing session with httpbin...")
        response = session.get('https://httpbin.org/ip', timeout=10)
        print(f"[DEBUG] Session test OK: {response.json()}")
        
        print("[DEBUG] Creating YouTubeTranscriptApi with session...")
        api = YouTubeTranscriptApi(http_client=session)
        
        print("[DEBUG] Calling api.list()...")
        transcript_list = api.list(video_id)
        
        print("[DEBUG] Looking for transcript...")
        transcript = transcript_list.find_transcript(['en'])
        
        print("[DEBUG] Fetching transcript...")
        data = transcript.fetch()
        
        text = " ".join([entry['text'] for entry in data[:5]])
        print(f"✅ Success! First 5 entries: {text[:100]}...")
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {str(e)[:200]}...")
    
    print()


if __name__ == "__main__":
    test_direct_proxy()
    test_youtube_api_without_proxy()
    test_youtube_api_with_proxy()
    test_session_with_proxy()
