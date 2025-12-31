"""
リトライハンドラー

リトライロジックを共通化し、エラー時の再試行処理を統一的に管理します。
"""
import time
from typing import Callable, Any, Optional
from .logger import setup_logger
from .exceptions import RateLimitError, IPBlockingError

logger = setup_logger(__name__)


class RetryHandler:
    """リトライ処理を管理するクラス"""
    
    # デフォルトの待機時間（秒）
    DEFAULT_WAIT_TIME = 5
    RATE_LIMIT_WAIT_TIME = 60
    
    def __init__(self, max_retries: int = 3, backoff_factor: int = 2):
        """
        Args:
            max_retries: 最大リトライ回数
            backoff_factor: 指数バックオフの係数
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        error_handler: Optional[Callable[[Exception, int], bool]] = None,
        **kwargs
    ) -> Any:
        """
        関数を実行し、失敗時には指数バックオフでリトライする
        
        Args:
            func: 実行する関数
            *args: 関数の位置引数
            error_handler: エラーハンドラー関数。
                          (exception, attempt) を受け取り、
                          リトライを続けるべきならTrue、中断するならFalseを返す
            **kwargs: 関数のキーワード引数
            
        Returns:
            関数の実行結果
            
        Raises:
            最後の試行で発生した例外
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # カスタムエラーハンドラーがある場合は使用
                if error_handler:
                    should_retry = error_handler(e, attempt)
                    if not should_retry:
                        raise
                
                # 最後の試行の場合はリトライしない
                if attempt >= self.max_retries - 1:
                    logger.error(
                        f"Failed after {self.max_retries} attempts. "
                        f"Last error: {type(e).__name__} - {str(e)}"
                    )
                    raise
                
                # 待機時間を計算
                wait_time = self._calculate_wait_time(attempt, e)
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {type(e).__name__} - {str(e)}. "
                    f"Retrying in {wait_time} seconds..."
                )
                
                time.sleep(wait_time)
        
        # 理論上ここには到達しないが、念のため
        if last_exception:
            raise last_exception
    
    def _calculate_wait_time(self, attempt: int, error: Exception) -> int:
        """
        待機時間を計算する
        
        Args:
            attempt: 現在の試行回数（0から始まる）
            error: 発生した例外
            
        Returns:
            待機時間（秒）
        """
        # レート制限エラーの場合は長めに待機
        if isinstance(error, RateLimitError):
            if error.retry_after:
                return error.retry_after
            return self.RATE_LIMIT_WAIT_TIME
        
        # HTTP 429エラーを文字列から検出
        error_msg = str(error).lower()
        if '429' in error_msg or 'too many requests' in error_msg:
            return self.RATE_LIMIT_WAIT_TIME
        
        # IP制限エラーの場合はリトライしない（呼び出し側で処理）
        if isinstance(error, IPBlockingError):
            return 0
        
        # 指数バックオフ
        return self.DEFAULT_WAIT_TIME * (self.backoff_factor ** attempt)
