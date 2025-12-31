"""
カスタム例外クラス

YouTubeSummaryプロジェクトで使用する例外を定義します。
エラーハンドリングを明確化し、適切なエラー処理を可能にします。
"""


class YouTubeSummaryError(Exception):
    """YouTubeSummaryプロジェクトの基底例外クラス"""
    pass


class ConfigurationError(YouTubeSummaryError):
    """設定関連のエラー"""
    pass


class TranscriptError(YouTubeSummaryError):
    """字幕取得関連のエラー"""
    pass


class IPBlockingError(TranscriptError):
    """IP制限によるアクセス拒否エラー"""
    
    def __init__(self, video_id: str, message: str = None):
        self.video_id = video_id
        default_message = (
            f"YouTube is blocking requests from this IP address for video {video_id}. "
            "This is a known issue when running from cloud providers. "
            "Consider using a proxy or VPN."
        )
        super().__init__(message or default_message)


class RateLimitError(TranscriptError):
    """レート制限エラー (HTTP 429)"""
    
    def __init__(self, video_id: str, retry_after: int = None):
        self.video_id = video_id
        self.retry_after = retry_after
        message = f"Rate limit exceeded for video {video_id}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


class SummarizationError(YouTubeSummaryError):
    """要約生成関連のエラー"""
    pass


class EmailError(YouTubeSummaryError):
    """メール送信関連のエラー"""
    pass
