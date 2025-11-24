from src.email_template import create_youtube_style_html_body
from datetime import datetime

# Dummy data for testing
videos = [
    {
        'title': 'Test Video 1: AI Revolution',
        'channel_title': 'Tech Channel',
        'published_at': datetime.now().isoformat(),
        'url': 'https://youtube.com/watch?v=123',
        'duration': '10:00',
        'view_count': 15000,
        'thumbnail': 'https://via.placeholder.com/640x360',
        'summary': 'This is a summary of the first video. It discusses the latest advancements in AI.'
    },
    {
        'title': 'Test Video 2: Python Coding',
        'channel_title': 'Code Channel',
        'published_at': datetime.now().isoformat(),
        'url': 'https://youtube.com/watch?v=456',
        'duration': '5:30',
        'view_count': 5000,
        'thumbnail': 'https://via.placeholder.com/640x360',
        'summary': 'This video covers Python programming basics. It is very useful for beginners.'
    }
]

html_content = create_youtube_style_html_body(videos)

with open('test_dark_mode.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated test_dark_mode.html")
