import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from youtube_client import YouTubeClient
from summarizer import Summarizer
from email_sender import EmailSender

# Load environment variables
load_dotenv()

def create_html_body(videos):
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">直近のYouTube更新情報</h2>
    """
    
    for video in videos:
        # Extract summary with newlines replaced (f-strings can't contain backslashes)
        summary_html = video['summary'].replace('\n', '\u003cbr\u003e')
        html += f"""
        \u003cdiv style="border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px;"\u003e
            \u003ch3 style="margin-top: 0;"\u003e\u003ca href="{video['url']}" style="text-decoration: none; color: #1a0dab;"\u003e{video['title']}\u003c/a\u003e\u003c/h3\u003e
            \u003cdiv style="display: flex; gap: 15px; margin-bottom: 10px;"\u003e
                \u003cimg src="{video['thumbnail']}" alt="Thumbnail" style="width: 200px; height: auto; border-radius: 4px;"\u003e
                \u003cdiv style="font-size: 0.9em; color: #666;"\u003e
                    \u003cp style="margin: 2px 0;"\u003e📺 チャンネル: {video['channel_title']}\u003c/p\u003e
                    \u003cp style="margin: 2px 0;"\u003e⏱️ 長さ: {video['duration']}\u003c/p\u003e
                    \u003cp style="margin: 2px 0;"\u003e👀 再生回数: {video['view_count']:,}回\u003c/p\u003e
                    \u003cp style="margin: 2px 0;"\u003e📅 投稿: {datetime.fromisoformat(video['published_at'].replace('Z', '+00:00')).strftime('%Y/%m/%d %H:%M')}\u003c/p\u003e
                \u003c/div\u003e
            \u003c/div\u003e
            \u003cdiv style="background-color: #f9f9f9; padding: 10px; border-radius: 4px;"\u003e
                {summary_html}
            \u003c/div\u003e
        \u003c/div\u003e
        """
    
    html += """
    <p style="font-size: 0.8em; color: #888; text-align: center;">
        This email was generated automatically by YouTube Summary Agent.
    </p>
    </body>
    </html>
    """
    return html

def main():
    # Configuration
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GMAIL_USER = os.getenv('GMAIL_USER')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')

    # Load channel IDs from file
    channel_ids_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'channel_ids.txt')
    TARGET_CHANNEL_IDS = []
    
    if os.path.exists(channel_ids_file):
        print(f"Loading channel IDs from {channel_ids_file}")
        with open(channel_ids_file, 'r', encoding='utf-8') as f:
            TARGET_CHANNEL_IDS = [line.strip() for line in f if line.strip()]
    
    # Fallback to env var if file is empty or missing
    if not TARGET_CHANNEL_IDS:
        print("Loading channel IDs from environment variable")
        TARGET_CHANNEL_IDS = os.getenv('TARGET_CHANNEL_IDS', '').split(',')
        # Filter empty strings
        TARGET_CHANNEL_IDS = [cid for cid in TARGET_CHANNEL_IDS if cid]

    # Validation
    if not all([YOUTUBE_API_KEY, OPENAI_API_KEY, GMAIL_USER, GMAIL_APP_PASSWORD, TARGET_CHANNEL_IDS, EMAIL_RECIPIENT]):
        print("Error: Missing environment variables or channel IDs. Please check your .env file or channel_ids.txt.")
        sys.exit(1)

    # Initialize clients
    youtube_client = YouTubeClient(YOUTUBE_API_KEY)
    summarizer = Summarizer(OPENAI_API_KEY)
    email_sender = EmailSender(GMAIL_USER, GMAIL_APP_PASSWORD)

    print("Fetching recent videos...")
    videos = youtube_client.get_videos_from_channels(TARGET_CHANNEL_IDS)

    if not videos:
        print("No new videos found. Sending notification...")
        subject = "【YouTube要約】新着動画はありませんでした"
        body_text = "直近の更新はありませんでした。"
        body_html = "<html><body><p>直近の更新はありませんでした。</p></body></html>"
        email_sender.send_email(EMAIL_RECIPIENT, subject, body_text, body_html)
        return

    print(f"Found {len(videos)} new videos.")
    
    # YouTube IP制限を回避するため、処理する動画数を制限
    MAX_VIDEOS = 50
    if len(videos) > MAX_VIDEOS:
        print(f"Limiting to {MAX_VIDEOS} videos to avoid IP blocking")
        videos = videos[:MAX_VIDEOS]
    
    print(f"Processing {len(videos)} videos...")
    
    email_body_text = "直近の更新動画要約です。\n\n"

    for idx, video in enumerate(videos, 1):
        print(f"[{idx}/{len(videos)}] Processing: {video['title']} ({video['url']})")
        
        # YouTube IP制限を回避するため、各リクエストの間に遅延を追加
        if idx > 1:  # 最初の動画以降
            print(f"  Waiting 2 seconds to avoid IP blocking...")
            time.sleep(2)
        
        transcript = youtube_client.get_transcript(video['video_id'])
        
        if transcript:
            print("  Transcript found. Summarizing...")
            summary = summarizer.summarize(transcript)
        else:
            print("  No transcript found.")
            summary = "字幕が取得できなかったため、要約を作成できませんでした。"
        
        video['summary'] = summary

        email_body_text += f"■ {video['title']}\n"
        email_body_text += f"URL: {video['url']}\n"
        email_body_text += f"要約:\n{summary}\n"
        email_body_text += "-" * 30 + "\n\n"

    print("Sending email...")
    subject = f"【YouTube要約】{len(videos)}本の新着動画があります"
    email_body_html = create_html_body(videos)
    
    email_sender.send_email(EMAIL_RECIPIENT, subject, email_body_text, email_body_html)
    print("Done!")

if __name__ == "__main__":
    main()
