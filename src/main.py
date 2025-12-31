import sys
from typing import List, Dict, Any

from .config import Config
from .logger import setup_logger
from .youtube_client import YouTubeClient
from .summarizer import Summarizer
from .email_sender import EmailSender
from .email_template import create_youtube_style_html_body
from .video_processor import VideoProcessor
from .proxy_manager import ProxyManager

logger = setup_logger(__name__)


def send_notification(email_sender: EmailSender, videos: List[Dict[str, Any]], email_body_text: str):
    """
    メール通知を送信
    
    Args:
        email_sender: メール送信クラス
        videos: 処理した動画リスト
        email_body_text: プレーンテキストのメール本文
    """
    if not videos:
        logger.info("Sending 'no updates' notification...")
        subject = Config.EMAIL_NO_UPDATES_SUBJECT
        body_text = Config.EMAIL_NO_UPDATES_BODY
        body_html = f"<html><body><p>{Config.EMAIL_NO_UPDATES_BODY}</p></body></html>"
        email_sender.send_email(Config.EMAIL_RECIPIENT, subject, body_text, body_html)
    else:
        logger.info("Sending summary email...")
        subject = Config.EMAIL_SUBJECT_TEMPLATE.format(count=len(videos))
        email_body_html = create_youtube_style_html_body(videos)
        email_sender.send_email(Config.EMAIL_RECIPIENT, subject, email_body_text, email_body_html)


def main():
    """メイン処理"""
    # 設定の検証
    if not Config.validate():
        logger.error("Missing environment variables or channel IDs. Please check your .env file or channel_ids.txt.")
        sys.exit(1)

    # プロキシマネージャーの初期化
    proxy_manager = None
    if Config.PROXY_ROTATION_ENABLED:
        proxy_manager = ProxyManager(
            proxy_file=Config.PROXY_LIST_FILE,
            webshare_token=Config.WEBSHARE_API_TOKEN,
            failure_threshold=Config.PROXY_FAILURE_THRESHOLD,
            disable_duration_minutes=Config.PROXY_DISABLE_DURATION
        )
        if proxy_manager.has_proxies():
            logger.info(f"Proxy rotation enabled with {len(proxy_manager.proxies)} proxies")
        else:
            logger.warning("Proxy rotation enabled but no proxies loaded")
            proxy_manager = None
    
    # クライアントの初期化
    youtube_client = YouTubeClient(
        Config.YOUTUBE_API_KEY, 
        Config.COOKIES_FILE,
        cache_dir=Config.CACHE_DIR,
        cache_expiry_days=Config.CACHE_EXPIRY_DAYS,
        max_retries=Config.MAX_RETRIES,
        backoff_factor=Config.BACKOFF_FACTOR,
        proxy_manager=proxy_manager,
        user_agent=Config.USER_AGENT
    )
    summarizer = Summarizer(Config.OPENAI_API_KEY)
    email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
    
    # VideoProcessorの初期化
    video_processor = VideoProcessor(
        youtube_client=youtube_client,
        summarizer=summarizer,
        processed_videos_file=Config.PROCESSED_VIDEOS_FILE,
        max_videos=Config.MAX_VIDEOS,
        retry_delay=Config.RETRY_DELAY
    )
    
    # チャンネルIDを取得
    channel_ids = Config.get_channel_ids()

    # 動画の取得とフィルタリング
    gen_ai_videos = video_processor.fetch_and_filter_videos(channel_ids)

    # 動画がない場合は通知を送信して終了
    if not gen_ai_videos:
        send_notification(email_sender, [], "")
        return

    # 動画の処理（字幕取得・要約生成）
    email_body_text = video_processor.process_videos(gen_ai_videos)

    # メール送信
    send_notification(email_sender, gen_ai_videos, email_body_text)
    
    # 処理済み動画IDを保存
    video_processor.mark_as_processed([v['video_id'] for v in gen_ai_videos])
    logger.info("Done!")


if __name__ == "__main__":
    main()

