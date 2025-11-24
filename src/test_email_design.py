import os
import sys
from dotenv import load_dotenv
from .email_template import create_youtube_style_html_body
from .email_sender import EmailSender

def test_design():
    # Load env
    load_dotenv()
    
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    recipient = os.getenv('EMAIL_RECIPIENT')
    
    if not all([gmail_user, gmail_password, recipient]):
        print("Error: Missing environment variables for email.")
        return

    # Mock data
    videos = [
        {
            'title': 'The Future of AI: What to Expect in 2025',
            'url': 'https://youtube.com/watch?v=example1',
            'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'channel_title': 'Tech Visionary',
            'duration': '15:30',
            'view_count': 125000,
            'published_at': '2023-11-23T10:00:00Z',
            'summary': 'This video explores the upcoming trends in Artificial Intelligence.\n\nKey insights include:\n- Generative AI advancements\n- Ethical considerations\n- Impact on job markets\n\nAction Plan:\n1. Stay updated with latest research.\n2. Experiment with new tools.'
        },
        {
            'title': 'Python 4.0: Rumors vs Reality',
            'url': 'https://youtube.com/watch?v=example2',
            'thumbnail': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            'channel_title': 'Coding Daily',
            'duration': '08:45',
            'view_count': 54000,
            'published_at': '2023-11-23T14:30:00Z',
            'summary': 'A deep dive into the speculation surrounding Python 4.0.\n\nThe video clarifies that there are no immediate plans for a breaking change version like Python 3 was.'
        }
    ]

    print("Generating HTML...")
    html = create_youtube_style_html_body(videos)
    
    # Save to file just in case
    output_file = 'test_youtube_style_email.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated {output_file}")

    print(f"Sending test email to {recipient}...")
    sender = EmailSender(gmail_user, gmail_password)
    sender.send_email(
        recipient, 
        "【デザイン確認】YouTube要約テスト (Mobile Optimized)", 
        "このメールはHTML形式でご覧ください。\n\n新しいデザインのテストです。", 
        html
    )
    print("Done!")

if __name__ == "__main__":
    test_design()
