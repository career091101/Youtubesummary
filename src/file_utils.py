"""
ファイル操作ユーティリティ

ファイルの読み書き操作を共通化し、コードの重複を削減します。
"""
import os
from typing import List, Set
from .logger import setup_logger

logger = setup_logger(__name__)


def read_lines(filepath: str, strip: bool = True) -> List[str]:
    """
    ファイルから行を読み込む
    
    Args:
        filepath: 読み込むファイルのパス
        strip: 各行の前後の空白を削除するかどうか
        
    Returns:
        ファイルの各行のリスト
    """
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            if strip:
                return [line.strip() for line in f if line.strip()]
            else:
                return [line for line in f]
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return []


def read_lines_as_set(filepath: str) -> Set[str]:
    """
    ファイルから行を読み込み、セットとして返す
    
    Args:
        filepath: 読み込むファイルのパス
        
    Returns:
        ファイルの各行のセット（重複なし）
    """
    lines = read_lines(filepath)
    return set(lines)


def append_lines(filepath: str, lines: List[str]) -> None:
    """
    ファイルに行を追加する
    
    Args:
        filepath: 書き込むファイルのパス
        lines: 追加する行のリスト
    """
    try:
        ensure_file_exists(filepath)
        with open(filepath, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
        logger.debug(f"Appended {len(lines)} lines to {filepath}")
    except Exception as e:
        logger.error(f"Error appending to file {filepath}: {e}")
        raise


def ensure_file_exists(filepath: str) -> None:
    """
    ファイルが存在することを保証する（存在しない場合は作成）
    
    Args:
        filepath: ファイルのパス
    """
    if not os.path.exists(filepath):
        # ディレクトリも作成
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # 空ファイルを作成
        open(filepath, 'a', encoding='utf-8').close()
        logger.debug(f"Created file: {filepath}")


def ensure_directory_exists(directory: str) -> None:
    """
    ディレクトリが存在することを保証する（存在しない場合は作成）
    
    Args:
        directory: ディレクトリのパス
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Created directory: {directory}")
