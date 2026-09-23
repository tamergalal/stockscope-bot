import os
os.environ["MODE"] = "webhook"
os.environ["WEBHOOK_URL"] = "https://example.onrender.com"
os.environ["PORT"] = "10000"
from stock_bot.config import settings
print("mode:", settings.mode)
print("webhook_url:", settings.webhook_url)
print("port:", settings.port)
assert settings.mode == "webhook" and settings.port == 10000
print("WEBHOOK CONFIG OK")
