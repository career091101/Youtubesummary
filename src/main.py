import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any

from .config import Config
from .logger import setup_logger
from .youtube_client import YouTubeClient
from .summarizer import Summarizer
from .email_sender import EmailSender
from .email_template import create_youtube_style_html_body

logger = setup_logger(__name__)

def fetch_videos(youtube_client: YouTubeClient, channel_ids: List[str]) -> List[Dict[str, Any]]:
    logger.info("Fetching recent videos...")
    videos = youtube_client.get_videos_from_channels(channel_ids)
    
    if not videos:
        logger.info("No new videos found.")
        return []
        
    logger.info(f"Found {len(videos)} new videos.")
    
    if len(videos) > Config.MAX_VIDEOS:
        logger.info(f"Limiting to {Config.MAX_VIDEOS} videos to avoid IP blocking")
        videos = videos[:Config.MAX_VIDEOS]
        
    return videos

def load_processed_videos() -> set:
    if os.path.exists(Config.PROCESSED_VIDEOS_FILE):
        with open(Config.PROCESSED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_processed_videos(video_ids: List[str]):
    with open(Config.PROCESSED_VIDEOS_FILE, 'a', encoding='utf-8') as f:
        for vid in video_ids:
            f.write(f"{vid}\n")

def is_gen_ai_content(video: Dict[str, Any], summarizer: Summarizer) -> bool:
    return summarizer.is_gen_ai_video(video['title'], video.get('description', ''))

def process_videos(videos: List[Dict[str, Any]], youtube_client: YouTubeClient, summarizer: Summarizer) -> str:
    logger.info(f"Processing {len(videos)} videos...")
    email_body_text = "直近の更新動画要約です。\n\n"
    
    for idx, video in enumerate(videos, 1):
        logger.info(f"[{idx}/{len(videos)}] Processing: {video['title']} ({video['url']})")
        
        # YouTube IP制限を回避するため、各リクエストの間に遅延を追加
        if idx > 1:
            logger.info(f"  Waiting {Config.RETRY_DELAY} seconds to avoid IP blocking...")
            time.sleep(Config.RETRY_DELAY)
        
        transcript = youtube_client.get_transcript(video['video_id'])
        
        if transcript:
            logger.info("  Transcript found. Summarizing...")
            summary = summarizer.summarize(transcript)
        else:
            logger.warning("  No transcript found.")
            summary = "字幕が取得できなかったため、要約を作成できませんでした。"
        
        video['summary'] = summary

        email_body_text += f"■ {video['title']}\n"
        email_body_text += f"URL: {video['url']}\n"
        email_body_text += f"要約:\n{summary}\n"
        email_body_text += "-" * 30 + "\n\n"
        
    return email_body_text

def send_notification(email_sender: EmailSender, videos: List[Dict[str, Any]], email_body_text: str):
    if not videos:
        logger.info("Sending 'no updates' notification...")
        subject = "【YouTube要約】新着動画はありませんでした"
        body_text = "直近の更新はありませんでした。"
        body_html = "<html><body><p>直近の更新はありませんでした。</p></body></html>"
        email_sender.send_email(Config.EMAIL_RECIPIENT, subject, body_text, body_html)
    else:
        logger.info("Sending summary email...")
        subject = f"【YouTube要約】{len(videos)}本の新着動画があります"
        email_body_html = create_youtube_style_html_body(videos)
        email_sender.send_email(Config.EMAIL_RECIPIENT, subject, email_body_text, email_body_html)

def main():
    # Validation
    if not Config.validate():
        logger.error("Missing environment variables or channel IDs. Please check your .env file or channel_ids.txt.")
        sys.exit(1)

    # Initialize clients
    proxies = {}
    if Config.PROXY_HTTP:
        proxies['http'] = Config.PROXY_HTTP
    if Config.PROXY_HTTPS:
        proxies['https'] = Config.PROXY_HTTPS
    
    youtube_client = YouTubeClient(
        Config.YOUTUBE_API_KEY, 
        Config.COOKIES_FILE,
        cache_dir=Config.CACHE_DIR,
        cache_expiry_days=Config.CACHE_EXPIRY_DAYS,
        max_retries=Config.MAX_RETRIES,
        backoff_factor=Config.BACKOFF_FACTOR,
        proxies=proxies if proxies else None
    )
    summarizer = Summarizer(Config.OPENAI_API_KEY)
    email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
    
    # Get Channel IDs
    channel_ids = Config.get_channel_ids()

    # Load processed video IDs
    processed_ids = load_processed_videos()
    logger.info(f"Loaded {len(processed_ids)} processed video IDs.")

    # Fetch Videos
    videos = fetch_videos(youtube_client, channel_ids)

    # Filter out processed videos
    new_videos = [v for v in videos if v['video_id'] not in processed_ids]
    logger.info(f"Filtered out {len(videos) - len(new_videos)} already processed videos.")
    
    # Filter for Generative AI content
    gen_ai_videos = []
    for v in new_videos:
        if is_gen_ai_content(v, summarizer):
            gen_ai_videos.append(v)
            logger.info(f"  [KEEP] {v['title']}")
        else:
            logger.info(f"  [SKIP] {v['title']}")

    logger.info(f"Filtered out {len(new_videos) - len(gen_ai_videos)} non-Generative AI videos.")

    if not gen_ai_videos:
        # Only send notification if we actually filtered out videos that were otherwise new
        # If no videos were found at all, fetch_videos returns [], so we are here too.
        # But if we found videos but they were all non-AI or processed, we might want to skip sending email?
        # The original requirement said "Notifications: Ensure an email is sent even if no new videos are found."
        # But user said "前回のメール配信した内容の動画は次回の配信で配信しないように"
        # Let's keep the "no updates" email for now, but maybe we should clarify if "no updates" means "no NEW AI updates".
        # For now, if no AI videos, send "no updates".
        send_notification(email_sender, [], "")
        return

    # Process Videos (Summarize)
    email_body_text = process_videos(gen_ai_videos, youtube_client, summarizer)

    # Send Email
    send_notification(email_sender, gen_ai_videos, email_body_text)
    
    # Save processed video IDs
    save_processed_videos([v['video_id'] for v in gen_ai_videos])
    logger.info("Done!")

if __name__ == "__main__":
    main()

