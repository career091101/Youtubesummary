"""
動画処理クラス

動画の取得、フィルタリング、処理を担当するクラスです。
main.pyのビジネスロジックをここに集約します。
"""
import time
from typing import List, Dict, Any, Set
from .logger import setup_logger
from .youtube_client import YouTubeClient
from .summarizer import Summarizer
from .file_utils import read_lines_as_set, append_lines

logger = setup_logger(__name__)


class VideoProcessor:
    """動画の取得、フィルタリング、処理を担当するクラス"""
    
    def __init__(
        self,
        youtube_client: YouTubeClient,
        summarizer: Summarizer,
        processed_videos_file: str,
        max_videos: int,
        retry_delay: int
    ):
        """
        Args:
            youtube_client: YouTube APIクライアント
            summarizer: 要約生成クラス
            processed_videos_file: 処理済み動画IDを保存するファイルパス
            max_videos: 1回の実行で処理する最大動画数
            retry_delay: 動画処理間の遅延時間（秒）
        """
        self.youtube_client = youtube_client
        self.summarizer = summarizer
        self.processed_videos_file = processed_videos_file
        self.max_videos = max_videos
        self.retry_delay = retry_delay
        self.processed_ids = self._load_processed_videos()
    
    def _load_processed_videos(self) -> Set[str]:
        """処理済み動画IDを読み込む"""
        processed_ids = read_lines_as_set(self.processed_videos_file)
        logger.info(f"Loaded {len(processed_ids)} processed video IDs.")
        return processed_ids
    
    def fetch_and_filter_videos(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
        """
        チャンネルから動画を取得し、フィルタリングする
        
        Args:
            channel_ids: 対象チャンネルIDのリスト
            
        Returns:
            フィルタリング後の動画リスト
        """
        # 動画を取得
        logger.info("Fetching recent videos...")
        videos = self.youtube_client.get_videos_from_channels(channel_ids)
        
        if not videos:
            logger.info("No new videos found.")
            return []
        
        logger.info(f"Found {len(videos)} new videos.")
        
        # 未処理の動画のみをフィルタリング
        new_videos = self.filter_new_videos(videos)
        
        # 生成AI関連の動画のみをフィルタリング
        gen_ai_videos = self.filter_gen_ai_videos(new_videos)
        
        # 最大動画数で制限
        if len(gen_ai_videos) > self.max_videos:
            logger.info(f"Limiting to {self.max_videos} AI videos to avoid IP blocking")
            gen_ai_videos = gen_ai_videos[:self.max_videos]
        
        return gen_ai_videos
    
    def filter_new_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        未処理の動画のみをフィルタリング
        
        Args:
            videos: 動画リスト
            
        Returns:
            未処理の動画リスト
        """
        new_videos = [v for v in videos if v['video_id'] not in self.processed_ids]
        filtered_count = len(videos) - len(new_videos)
        
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} already processed videos.")
        
        return new_videos
    
    def filter_gen_ai_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成AI関連の動画のみをフィルタリング
        
        Args:
            videos: 動画リスト
            
        Returns:
            生成AI関連の動画リスト
        """
        gen_ai_videos = []
        
        for video in videos:
            if self._is_gen_ai_content(video):
                gen_ai_videos.append(video)
                logger.info(f"  [KEEP] {video['title']}")
            else:
                logger.info(f"  [SKIP] {video['title']}")
        
        filtered_count = len(videos) - len(gen_ai_videos)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} non-Generative AI videos.")
        
        return gen_ai_videos
    
    def _is_gen_ai_content(self, video: Dict[str, Any]) -> bool:
        """
        動画が生成AI関連かどうかを判定
        
        Args:
            video: 動画情報
            
        Returns:
            生成AI関連ならTrue
        """
        return self.summarizer.is_gen_ai_video(
            video['title'],
            video.get('description', '')
        )
    
    def process_videos(self, videos: List[Dict[str, Any]]) -> str:
        """
        動画を処理（字幕取得・要約生成）
        
        Args:
            videos: 処理する動画リスト
            
        Returns:
            プレーンテキストのメール本文
        """
        logger.info(f"Processing {len(videos)} videos...")
        email_body_text = "直近の更新動画要約です。\n\n"
        
        for idx, video in enumerate(videos, 1):
            logger.info(f"[{idx}/{len(videos)}] Processing: {video['title']} ({video['url']})")
            
            # IP制限を回避するため、各リクエストの間に遅延を追加
            if idx > 1:
                logger.info(f"  Waiting {self.retry_delay} seconds to avoid IP blocking...")
                time.sleep(self.retry_delay)
            
            # 字幕を取得
            transcript = self.youtube_client.get_transcript(video['video_id'])
            
            # 要約を生成
            if transcript:
                logger.info("  Transcript found. Summarizing...")
                summary = self.summarizer.summarize(transcript)
            else:
                logger.warning("  No transcript found.")
                summary = "字幕が取得できなかったため、要約を作成できませんでした。"
            
            video['summary'] = summary
            
            # プレーンテキスト本文を構築
            email_body_text += f"■ {video['title']}\n"
            email_body_text += f"URL: {video['url']}\n"
            email_body_text += f"要約:\n{summary}\n"
            email_body_text += "-" * 30 + "\n\n"
        
        return email_body_text
    
    def mark_as_processed(self, video_ids: List[str]) -> None:
        """
        動画を処理済みとしてマーク
        
        Args:
            video_ids: 処理済みとしてマークする動画IDのリスト
        """
        append_lines(self.processed_videos_file, video_ids)
        # メモリ上のセットも更新
        self.processed_ids.update(video_ids)
        logger.info(f"Marked {len(video_ids)} videos as processed.")
