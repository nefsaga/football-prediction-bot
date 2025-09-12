import os
from dotenv import load_dotenv

# .env dosyasını yükle (local development için)
load_dotenv()

# Railway environment variables (production) veya local .env (development)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "8245448557:AAHnX7ShiF0tjDR7_x9rUIK-BxmbXw7lXu8")
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', "1076045011")

# Bot Settings
BOT_NAME = "Football Predictions Bot v1.0"
TIMEZONE = "Europe/Istanbul"

# Debug mod
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Deployment kontrolü
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN environment variable gerekli!")

if not CHAT_ID:
    raise ValueError("❌ TELEGRAM_CHAT_ID environment variable gerekli!")

# Railway deployment detection
RAILWAY = os.getenv('RAILWAY_ENVIRONMENT_NAME') is not None

if RAILWAY:
    print("🚂 Railway deployment tespit edildi")
else:
    print("💻 Local development mode")

print(f"✅ Config yüklendi - Bot: {BOT_NAME}")
print(f"🤖 Token: {TELEGRAM_TOKEN[:10]}...")
print(f"👤 Chat ID: {CHAT_ID}")