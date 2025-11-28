import sys
import os
from src.config import Config
from src.email_sender import EmailSender

def test_email():
    if not Config.validate():
        print("Config validation failed.")
        return

    sender = EmailSender(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
    recipient = Config.EMAIL_RECIPIENT
    
    print(f"Attempting to send test email to {recipient}...")
    
    try:
        sender.send_email(
            recipient, 
            "【テスト】YouTube要約システムの配信確認", 
            "これはテストメールです。このメールが届けば、メール送信機能は正常です。\n\n18:00と22:00の配信が届いていない場合、PCがスリープしていた可能性があります。",
            "<html><body><p>これはテストメールです。このメールが届けば、メール送信機能は正常です。</p><p>18:00と22:00の配信が届いていない場合、PCがスリープしていた可能性があります。</p></body></html>"
        )
        print("Test email sent successfully.")
    except Exception as e:
        print(f"Failed to send test email: {e}")

if __name__ == "__main__":
    test_email()
