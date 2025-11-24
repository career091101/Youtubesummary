import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from src.youtube_client import YouTubeClient

class TestShortsExclusion(unittest.TestCase):
    @patch('src.youtube_client.build')
    def test_get_videos_excludes_shorts(self, mock_build):
        # Setup mock
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        
        # Mock channel list response
        mock_youtube.channels().list().execute.return_value = {
            'items': [{'contentDetails': {'relatedPlaylists': {'uploads': 'UPLOADS_ID'}}}]
        }
        
        # Mock playlist items response (recent videos)
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(hours=1)).isoformat()
        
        mock_youtube.playlistItems().list().execute.return_value = {
            'items': [
                {
                    'snippet': {
                        'publishedAt': recent_date,
                        'resourceId': {'videoId': 'LONG_VIDEO_ID'},
                        'title': 'Long Video',
                        'channelTitle': 'Test Channel',
                        'thumbnails': {'high': {'url': 'http://example.com/long.jpg'}, 'default': {'url': 'http://example.com/long_def.jpg'}}
                    }
                },
                {
                    'snippet': {
                        'publishedAt': recent_date,
                        'resourceId': {'videoId': 'SHORT_VIDEO_ID'},
                        'title': 'Short Video',
                        'channelTitle': 'Test Channel',
                        'thumbnails': {'high': {'url': 'http://example.com/short.jpg'}, 'default': {'url': 'http://example.com/short_def.jpg'}}
                    }
                }
            ]
        }
        
        # Mock video details response (duration)
        # We need to handle multiple calls to videos().list()
        def video_details_side_effect(**kwargs):
            vid = kwargs.get('id')
            mock_resp = MagicMock()
            if vid == 'LONG_VIDEO_ID':
                mock_resp.execute.return_value = {
                    'items': [{
                        'contentDetails': {'duration': 'PT5M30S'}, # 5 min 30 sec
                        'statistics': {'viewCount': '1000'}
                    }]
                }
            elif vid == 'SHORT_VIDEO_ID':
                mock_resp.execute.return_value = {
                    'items': [{
                        'contentDetails': {'duration': 'PT59S'}, # 59 sec
                        'statistics': {'viewCount': '500'}
                    }]
                }
            return mock_resp

        mock_youtube.videos().list.side_effect = video_details_side_effect

        # Initialize client
        client = YouTubeClient('FAKE_API_KEY')
        
        # Run method
        print("\n--- Running Shorts Exclusion Test ---")
        videos = client.get_videos_from_channels(['CHANNEL_ID'])
        
        # Assertions
        print(f"Found {len(videos)} videos.")
        for v in videos:
            print(f"Kept video: {v['title']} ({v['duration']})")
            
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['video_id'], 'LONG_VIDEO_ID')
        print("--- Test Passed: Short video was excluded ---")

if __name__ == '__main__':
    unittest.main()
