import os, requests

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    @classmethod
    def from_env(cls):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            return cls(token, chat_id)
        return None

    def send_message(self, title: str, message: str):
        text = f"{title}\n{message}"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": text, "disable_web_page_preview": True}
        r = requests.post(url, json=data, timeout=5)
        r.raise_for_status()
        return True
