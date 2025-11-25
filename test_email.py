#!/usr/bin/env python3
"""
Test script to send a sample email with the new template design.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.email_sender import EmailSender
from src.email_template import create_youtube_style_html_body
from datetime import datetime

def main():
    # Sample video data
    sample_video = {
        'video_id': 'pe4izKdMveA',
        'title': '【最高です】Claude Opus 4.5 モデルが新登場！開発・エージェント性能で圧倒的だったので解説します',
        'url': 'https://www.youtube.com/watch?v=pe4izKdMveA',
        'thumbnail': 'https://i.ytimg.com/vi/pe4izKdMveA/mqdefault.jpg',
        'duration': '10:23',
        'channel_title': 'AIガイド',
        'view_count': 15234,
        'published_at': '2025-11-25T01:00:00Z',
        'summary': 'Claude Opus 4.5は、Anthropicが新たにリリースした最新のAIモデルです。このモデルは、特に開発タスクやエージェント機能において圧倒的な性能を発揮します。\\n\\n主な特徴として、コード生成の精度が大幅に向上し、複雑なプログラミングタスクにも対応可能になりました。また、マルチステップの推論能力が強化され、より高度な問題解決が可能です。\\n\\nベンチマークテストでは、従来モデルを大きく上回る結果を示しており、実用性の高さが証明されています。開発者にとって非常に有用なツールとなるでしょう。'
    }
    
    # Create email
    email_sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
    
    subject = "【テスト】新しいメールデザインのテスト"
    
    # Plain text version
    body_text = f"""
テストメール - 新しいデザインの確認

■ {sample_video['title']}
URL: {sample_video['url']}
要約:
{sample_video['summary']}
"""
    
    # HTML version
    body_html = create_youtube_style_html_body([sample_video])
    
    # Send email
    print(f"Sending test email to: {Config.EMAIL_RECIPIENT}")
    email_sender.send_email(Config.EMAIL_RECIPIENT, subject, body_text, body_html)
    print("Test email sent successfully!")

if __name__ == "__main__":
    main()
