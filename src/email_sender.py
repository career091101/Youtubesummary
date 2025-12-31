import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from .logger import setup_logger
from .exceptions import EmailError

logger = setup_logger(__name__)

class EmailSender:
    def __init__(self, gmail_user: str, gmail_password: str):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password

    def send_email(self, recipient: str, subject: str, body_text: str, body_html: Optional[str] = None):
        """
        Sends an email using Gmail SMTP. Supports both plain text and HTML.
        
        Args:
            recipient: メール受信者のアドレス
            subject: メール件名
            body_text: プレーンテキストの本文
            body_html: HTML形式の本文（オプション）
            
        Raises:
            EmailError: メール送信に失敗した場合
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = self.gmail_user
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach plain text
        msg.attach(MIMEText(body_text, 'plain'))
        
        # Attach HTML if provided
        if body_html:
            msg.attach(MIMEText(body_html, 'html'))

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent successfully to {recipient}")
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed. Please check your Gmail credentials: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred while sending email: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error while sending email: {e}"
            logger.error(error_msg)
            raise EmailError(error_msg) from e

