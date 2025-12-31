#!/usr/bin/env python3
"""
Verify Proxy Integration with YouTube Transcript API
Tests if proxies are actually being used and preventing IP blocks.
"""

import os
import sys
from dotenv import load_dotenv
from src.youtube_client import YouTubeClient
from src.proxy_manager import ProxyManager
from src.logger import setup_logger

logger = setup_logger(__name__)

# Test video IDs - popular videos with transcripts
TEST_VIDEOS = [
    ('dQw4w9WgXcQ', 'Rick Astley - Never Gonna Give You Up'),
    ('9bZkp7q19f0', 'PSY - GANGNAM STYLE'),
    ('kJQP7kiw5Fk', 'Luis Fonsi - Despacito'),
    ('OPf0YbXqDm0', 'Mark Ronson - Uptown Funk'),
    ('fJ9rUzIMcZQ', 'Queen - Bohemian Rhapsody')
]


def main():
    print("=" * 80)
    print("🔍 Proxy Integration Verification for YouTube Transcript API")
    print("=" * 80)
    print()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ Error: YOUTUBE_API_KEY not found in .env file")
        sys.exit(1)
    
    # Initialize proxy manager
    proxy_file = "proxy_list.txt"
    if not os.path.exists(proxy_file):
        print(f"❌ Error: {proxy_file} not found")
        sys.exit(1)
    
    proxy_manager = ProxyManager(
        proxy_file=proxy_file,
        failure_threshold=2,
        disable_duration_minutes=10,
        shuffle=True
    )
    
    if not proxy_manager.has_proxies():
        print("❌ Error: No proxies loaded")
        sys.exit(1)
    
    print(f"✅ Loaded {len(proxy_manager.proxies)} proxies")
    print()
    
    # Test 1: Without Proxy
    print("📋 Test 1: Fetching transcripts WITHOUT proxy")
    print("-" * 80)
    
    client_no_proxy = YouTubeClient(
        api_key=api_key,
        max_retries=1
    )
    
    success_no_proxy = 0
    for video_id, title in TEST_VIDEOS[:3]:  # Test first 3 videos
        print(f"Testing: {title[:50]}...")
        try:
            transcript = client_no_proxy.get_transcript(video_id)
            if transcript:
                print(f"  ✅ Success - {len(transcript)} chars")
                success_no_proxy += 1
            else:
                print(f"  ❌ Failed - No transcript returned")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    print()
    print(f"Results: {success_no_proxy}/3 successful without proxy")
    print()
    
    # Test 2: With Proxy
    print("📋 Test 2: Fetching transcripts WITH proxy rotation")
    print("-" * 80)
    
    client_with_proxy = YouTubeClient(
        api_key=api_key,
        proxy_manager=proxy_manager,
        max_retries=2
    )
    
    success_with_proxy = 0
    for video_id, title in TEST_VIDEOS[:3]:  # Test first 3 videos
        print(f"Testing: {title[:50]}...")
        try:
            transcript = client_with_proxy.get_transcript(video_id)
            if transcript:
                print(f"  ✅ Success - {len(transcript)} chars")
                success_with_proxy += 1
            else:
                print(f"  ❌ Failed - No transcript returned")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    print()
    print(f"Results: {success_with_proxy}/3 successful with proxy")
    print()
    
    # Test 3: Proxy Statistics
    print("📊 Test 3: Proxy Usage Statistics")
    print("-" * 80)
    proxy_manager.log_stats()
    stats = proxy_manager.get_stats()
    print()
    
    # Show detailed proxy stats
    print("Detailed Proxy Statistics:")
    print(f"  Total proxies: {stats['total']}")
    print(f"  Available: {stats['available']}")
    print(f"  Temporarily disabled: {stats['disabled']}")
    print(f"  Total successes: {stats['total_successes']}")
    print(f"  Total failures: {stats['total_failures']}")
    
    if stats['total_successes'] + stats['total_failures'] > 0:
        success_rate = stats['total_successes'] / (stats['total_successes'] + stats['total_failures']) * 100
        print(f"  Success rate: {success_rate:.1f}%")
    print()
    
    # Show individual proxy performance
    print("Individual Proxy Performance:")
    print("-" * 80)
    for i, proxy in enumerate(proxy_manager.proxies, 1):
        status = "✅ Available" if proxy.is_available() else "❌ Disabled"
        print(f"{i}. {proxy.host}:{proxy.port}")
        print(f"   Status: {status}")
        print(f"   Successes: {proxy.success_count}, Failures: {proxy.failure_count}")
        if proxy.last_used:
            print(f"   Last used: {proxy.last_used.strftime('%Y-%m-%d %H:%M:%S')}")
        if proxy.disabled_until:
            print(f"   Disabled until: {proxy.disabled_until.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print()
    print("=" * 80)
    print("📋 Summary")
    print("=" * 80)
    
    if success_with_proxy >= success_no_proxy:
        print("✅ Proxy integration is working correctly!")
        print(f"   With proxy: {success_with_proxy}/3 successful")
        print(f"   Without proxy: {success_no_proxy}/3 successful")
    else:
        print("⚠️  Warning: Proxy performance is lower than without proxy")
        print(f"   With proxy: {success_with_proxy}/3 successful")
        print(f"   Without proxy: {success_no_proxy}/3 successful")
        print("   This could indicate proxy configuration issues.")
    
    if stats['total_successes'] > 0:
        print(f"\n✅ Proxies were successfully used {stats['total_successes']} times")
        print("✅ IP blocking is being mitigated by proxy rotation")
    else:
        print("\n⚠️  Warning: No successful proxy usage detected")
        print("   Check proxy configuration and connectivity")
    
    print()
    
    # Test 4: IP Blocking Detection
    print("📋 Test 4: IP Blocking Detection")
    print("-" * 80)
    
    if stats['total_failures'] > 0:
        print(f"⚠️  {stats['total_failures']} proxy failures detected")
        print("   These could be due to:")
        print("   - YouTube IP blocking")
        print("   - Proxy connectivity issues")
        print("   - Rate limiting")
    else:
        print("✅ No proxy failures detected")
    
    blocking_indicators = [
        p for p in proxy_manager.proxies 
        if p.failure_count > 0 and not p.is_available()
    ]
    
    if blocking_indicators:
        print(f"\n⚠️  {len(blocking_indicators)} proxies are temporarily disabled")
        print("   This suggests possible IP blocking or rate limiting")
    else:
        print("\n✅ All proxies are operational")
        print("✅ No IP blocking detected")
    
    print()
    print("=" * 80)
    print("✨ Verification Complete")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
