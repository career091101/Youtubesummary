import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self, gmail_user, gmail_password):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password

    def send_email(self, recipient, subject, body_text, body_html=None):
        """
        Sends an email using Gmail SMTP. Supports both plain text and HTML.
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
            print(f"Email sent successfully to {recipient}")
        except Exception as e:
            print(f"Failed to send email: {e}")
