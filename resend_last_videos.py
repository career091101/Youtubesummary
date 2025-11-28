import os
import sys
from typing import List, Dict, Any
from googleapiclient.discovery import build
from src.config import Config
from src.email_sender import EmailSender
from src.summarizer import Summarizer
from src.youtube_client import YouTubeClient
from src.email_template import create_youtube_style_html_body

def get_last_processed_ids(limit: int = 10) -> List[str]:
    if not os.path.exists(Config.PROCESSED_VIDEOS_FILE):
        return []
    
    with open(Config.PROCESSED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    return lines[-limit:]

def fetch_video_details(youtube_client: YouTubeClient, video_ids: List[str]) -> List[Dict[str, Any]]:
    videos = []
    # YouTube API allows up to 50 IDs per request
    response = youtube_client.youtube.videos().list(
        id=','.join(video_ids),
        part='snippet,contentDetails,statistics'
    ).execute()

    for item in response.get('items', []):
        snippet = item['snippet']
        video_id = item['id']
        
        # Parse duration (simple version)
        duration = item['contentDetails']['duration']
        
        videos.append({
            'video_id': video_id,
            'title': snippet['title'],
            'channel_title': snippet['channelTitle'],
            'published_at': snippet['publishedAt'],
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'duration': duration, # Raw duration for now
            'view_count': int(item['statistics'].get('viewCount', 0)),
            'thumbnail': snippet['thumbnails'].get('high', snippet['thumbnails']['default'])['url']
        })
    return videos

def resend_email():
    if not Config.validate():
        print("Config validation failed.")
        return

    # Initialize clients
    youtube_client = YouTubeClient(Config.YOUTUBE_API_KEY)
    summarizer = Summarizer(Config.OPENAI_API_KEY)
    email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)

    # Get last 10 IDs
    video_ids = get_last_processed_ids(10)
    if not video_ids:
        print("No processed videos found.")
        return
    
    print(f"Found {len(video_ids)} video IDs to resend.")

    # Fetch details
    videos = fetch_video_details(youtube_client, video_ids)
    
    # Generate summaries
    print("Generating summaries...")
    email_body_text = "【再送】直近の更新動画要約です。\n\n"
    
    for video in videos:
        print(f"Summarizing: {video['title']}")
        transcript = youtube_client.get_transcript(video['video_id'])
        if transcript:
            summary = summarizer.summarize(transcript)
        else:
            summary = "字幕が取得できなかったため、要約を作成できませんでした。"
        
        video['summary'] = summary
        
        email_body_text += f"■ {video['title']}\n"
        email_body_text += f"URL: {video['url']}\n"
        email_body_text += f"要約:\n{summary}\n"
        email_body_text += "-" * 30 + "\n\n"

    # Send Email
    subject = f"【再送】{len(videos)}本の新着動画があります"
    email_body_html = create_youtube_style_html_body(videos)
    
    print("Sending email...")
    email_sender.send_email(Config.EMAIL_RECIPIENT, subject, email_body_text, email_body_html)
    print("Done.")

if __name__ == "__main__":
    resend_email()
