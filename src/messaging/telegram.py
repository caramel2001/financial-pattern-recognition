import requests
from src.utils.config import settings

class BaseTelegram:
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = settings['TELEBOT_KEY']
        self.TELEGRAM_CHAT_ID = settings['TELEBOT_CHATID']
    
    def send_telegram_message(self, message: str):
        """Sends a message to the configured Telegram chat."""
        print("Sending Telegram message:", message)
        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": self.TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)