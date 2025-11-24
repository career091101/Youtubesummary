#!/usr/bin/env python3
"""
メール配信テストスクリプト
実際のメール送信機能をテストします。
"""

import sys
import os
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.config import Config
from src.email_sender import EmailSender
from src.email_template import create_youtube_style_html_body

def create_test_videos():
    """テスト用の動画データを作成"""
    return [
        {
            'video_id': 'test_video_1',
            'title': 'Gemini 2.0の新機能紹介 - 生成AIの最新トレンド',
            'url': 'https://www.youtube.com/watch?v=test_video_1',
            'channel_title': 'AI Tech Channel',
            'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'duration': '12:34',
            'view_count': 125000,
            'published_at': '2025-11-24T10:00:00Z',
            'summary': 'この動画では、Gemini 2.0の最新機能について詳しく解説しています。\n\n主なポイント:\n• マルチモーダル機能の強化\n• より高速な応答時間\n• 日本語処理の精度向上\n• 新しいAPI機能の追加\n\nこれらの機能により、開発者はより柔軟なAIアプリケーションを構築できるようになります。'
        },
        {
            'video_id': 'test_video_2',
            'title': 'ChatGPT-5の実力を検証してみた',
            'url': 'https://www.youtube.com/watch?v=test_video_2',
            'channel_title': 'Tech Review Japan',
            'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'duration': '8:45',
            'view_count': 89000,
            'published_at': '2025-11-23T15:30:00Z',
            'summary': 'ChatGPT-5の性能を様々な観点から検証しました。\n\n検証項目:\n• コーディング能力\n• 論理的思考力\n• クリエイティブな文章生成\n• 多言語対応\n\n結論として、前バージョンと比較して大幅な性能向上が確認できました。'
        },
        {
            'video_id': 'test_video_3',
            'title': 'AI画像生成の最新技術 - Stable Diffusion 3.0',
            'url': 'https://www.youtube.com/watch?v=test_video_3',
            'channel_title': 'Creative AI Lab',
            'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'duration': '15:20',
            'view_count': 234000,
            'published_at': '2025-11-22T09:00:00Z',
            'summary': 'Stable Diffusion 3.0の新機能と実用例を紹介します。\n\n新機能:\n• より高解像度な画像生成\n• テキストプロンプトの理解力向上\n• 生成速度の改善\n• より自然な人物描写\n\n実際の使用例を通じて、クリエイティブワークフローへの統合方法も解説しています。'
        }
    ]

def test_email_delivery():
    """メール配信のテスト"""
    print("=" * 60)
    print("メール配信テスト")
    print("=" * 60)
    
    # 環境変数の確認
    if not Config.validate():
        print("❌ エラー: 環境変数が設定されていません")
        print("   .envファイルを確認してください")
        return False
    
    print(f"\n📧 送信先: {Config.EMAIL_RECIPIENT}")
    print(f"📨 送信元: {Config.GMAIL_USER}")
    
    # テストデータの作成
    test_videos = create_test_videos()
    print(f"\n📹 テスト動画数: {len(test_videos)}本")
    
    # HTMLボディの生成
    print("\n🎨 HTMLメールテンプレートを生成中...")
    html_body = create_youtube_style_html_body(test_videos)
    
    # テキストボディの生成
    text_body = "YouTube要約テストメール\n\n"
    for video in test_videos:
        text_body += f"■ {video['title']}\n"
        text_body += f"URL: {video['url']}\n"
        text_body += f"要約:\n{video['summary']}\n"
        text_body += "-" * 30 + "\n\n"
    
    # メール送信
    print("\n📤 メールを送信中...")
    try:
        email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
        subject = f"【テスト配信】YouTube要約 - {len(test_videos)}本の動画"
        
        email_sender.send_email(
            recipient=Config.EMAIL_RECIPIENT,
            subject=subject,
            body_text=text_body,
            body_html=html_body
        )
        
        print("\n✅ メール送信成功!")
        print(f"   件名: {subject}")
        print(f"   送信先: {Config.EMAIL_RECIPIENT}")
        print(f"\n💡 メールボックスを確認してください")
        return True
        
    except Exception as e:
        print(f"\n❌ メール送信失敗: {e}")
        return False

def test_empty_notification():
    """新着動画なしの通知テスト"""
    print("\n" + "=" * 60)
    print("新着動画なし通知のテスト")
    print("=" * 60)
    
    try:
        email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
        subject = "【テスト配信】YouTube要約 - 新着動画はありませんでした"
        body_text = "直近の更新はありませんでした。"
        body_html = "<html><body><p>直近の更新はありませんでした。</p></body></html>"
        
        print("\n📤 メールを送信中...")
        email_sender.send_email(
            recipient=Config.EMAIL_RECIPIENT,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )
        
        print("\n✅ メール送信成功!")
        print(f"   件名: {subject}")
        return True
        
    except Exception as e:
        print(f"\n❌ メール送信失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("\n🚀 YouTube要約メール配信テストを開始します\n")
    
    # テスト1: 通常のメール配信
    result1 = test_email_delivery()
    
    # テスト2: 新着なし通知
    print("\n")
    response = input("新着動画なし通知もテストしますか? (y/n): ")
    if response.lower() == 'y':
        result2 = test_empty_notification()
    else:
        result2 = True
        print("スキップしました")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"通常配信テスト: {'✅ 成功' if result1 else '❌ 失敗'}")
    print(f"新着なし通知テスト: {'✅ 成功' if result2 else '❌ 失敗'}")
    print("=" * 60)
    
    if result1 and result2:
        print("\n🎉 すべてのテストが成功しました!")
        return 0
    else:
        print("\n⚠️  一部のテストが失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
