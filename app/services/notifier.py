# app/services/notifier.py
from abc import ABC, abstractmethod
from typing import Dict
import aiosmtplib
from email.mime.text import MIMEText
from ..core.config import settings

class NotificationStrategy(ABC):
    """Abstract base class for notification strategies"""
    
    @abstractmethod
    async def notify(self, message: str) -> None:
        """Send notification"""
        pass

class ConsoleNotifier(NotificationStrategy):
    """Simple console notification implementation"""
    
    async def notify(self, message: str) -> None:
        """Print notification to console"""
        print("\n=== Scraping Notification ===")
        print(message)
        print("===========================\n")

class EmailNotifier(NotificationStrategy):
    """Email notification implementation using async SMTP"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.username = settings.EMAIL_SENDER
        self.password = settings.EMAIL_PASSWORD
        self.from_email = settings.EMAIL_SENDER
        self.to_email = settings.EMAIL_RECIPIENT

    async def notify(self, message: str) -> None:
        """Send notification via email"""
        msg = MIMEText(message)
        msg['Subject'] = 'Scraping Notification'
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        try:
            if self.port == 465:
                smtp = aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.port,
                    use_tls=True,
                    validate_certs=True
                )
            else:
                smtp = aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.port,
                    use_tls=False, 
                    validate_certs=True
                )

            await smtp.connect()
            
            if self.port == 587:
                await smtp.starttls()
                
            await smtp.login(self.username, self.password)
            await smtp.send_message(msg)
            await smtp.quit()
                
            print(f"Email sent to {self.to_email} successfully.")
            
        except Exception as e:
            error_message = f"Failed to send email: {str(e)}"
            print(error_message)
            await ConsoleNotifier().notify(f"Scraping failed: {str(e)}")
            raise Exception(error_message)
