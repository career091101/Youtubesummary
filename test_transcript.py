import os
from dotenv import load_dotenv
from src.youtube_client import YouTubeClient

# Load environment variables
load_dotenv()

def test_transcript_fetch():
    """Test the transcript fetching functionality"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ Error: YOUTUBE_API_KEY not found in environment variables")
        return
    
    client = YouTubeClient(api_key)
    
    # Test videos with different language transcripts
    test_cases = [
        {
            'name': 'Japanese video with Japanese subtitles',
            'video_id': 'jNQXAC9IVRw',  # "Me at the zoo" - first YouTube video
            'expected_language': 'en'  # This video likely has English subtitles
        },
        {
            'name': 'Popular video with multiple language support',
            'video_id': 'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
            'expected_language': 'en'
        }
    ]
    
    print("=" * 60)
    print("Testing YouTube Transcript Fetching")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"   Video ID: {test_case['video_id']}")
        print(f"   URL: https://www.youtube.com/watch?v={test_case['video_id']}")
        
        try:
            transcript = client.get_transcript(test_case['video_id'])
            
            if transcript:
                print(f"   ✅ SUCCESS: Retrieved transcript")
                print(f"   📊 Length: {len(transcript)} characters")
                print(f"   📄 Preview (first 150 chars):")
                print(f"      {transcript[:150]}...")
            else:
                print(f"   ⚠️  No transcript available for this video")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    test_transcript_fetch()
