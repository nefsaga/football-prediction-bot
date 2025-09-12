import os
import asyncio
from telegram_bot import TelegramFootballBot

def check_environment():
    """Environment variables kontrolü"""
    print("🔍 Environment variables kontrol ediliyor...")
    
    # Gerekli environment variables
    required_vars = {
        'TELEGRAM_TOKEN': 'Telegram bot token',
        'TELEGRAM_CHAT_ID': 'Telegram chat ID'
    }
    
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(f"  ❌ {var_name}: {description}")
        else:
            # Token/ID'yi kısmi göster (güvenlik için)
            if 'TOKEN' in var_name:
                display_value = f"{value[:10]}..."
            else:
                display_value = value
            print(f"  ✅ {var_name}: {display_value}")
    
    if missing_vars:
        print("\n❌ Eksik environment variables:")
        for var in missing_vars:
            print(var)
        print("\n🔧 Railway dashboard'da Environment Variables bölümüne ekleyin:")
        print("   TELEGRAM_TOKEN = your_bot_token")
        print("   TELEGRAM_CHAT_ID = your_chat_id")
        return False
    
    print("✅ Tüm environment variables mevcut")
    return True

def detect_environment():
    """Deployment environment tespit et"""
    railway_env = os.getenv('RAILWAY_ENVIRONMENT_NAME')
    railway_service = os.getenv('RAILWAY_SERVICE_NAME')
    
    if railway_env or railway_service:
        print("🚂 Railway deployment tespit edildi")
        print(f"   Environment: {railway_env or 'production'}")
        print(f"   Service: {railway_service or 'football-bot'}")
        return 'railway'
    else:
        print("💻 Local development mode tespit edildi")
        return 'local'

def main():
    """Railway entry point - Football Prediction Bot"""
    print("=" * 50)
    print("🤖 FOOTBALL PREDICTION BOT")
    print("🌍 Multi-League Advanced Analytics")
    print("🚀 Railway Deployment v1.0")
    print("=" * 50)
    
    # Environment detection
    env_type = detect_environment()
    
    # Environment variables kontrolü
    if not check_environment():
        print("\n💡 Çözüm:")
        if env_type == 'railway':
            print("1. Railway dashboard'a git")
            print("2. Project'ini seç")
            print("3. Variables sekmesine tıkla")
            print("4. Environment variables ekle")
        else:
            print("1. .env dosyası oluştur")
            print("2. TELEGRAM_TOKEN ve TELEGRAM_CHAT_ID ekle")
        exit(1)
    
    # System info
    print("\n📊 SİSTEM BİLGİLERİ:")
    print("   🏆 11 lig desteği (Premier League, La Liga, vb.)")
    print("   📡 Real-time fixture entegrasyonu (TheSportsDB)")
    print("   🎯 Advanced Poisson + Form algoritması")
    print("   📈 3 sezon veri + 4 sezon H2H analizi")
    print("   💰 Value bet analizi")
    print("   🤖 Telegram komut sistemi")
    
    # Bot başlatma
    print("\n🎯 Telegram bot başlatılıyor...")
    
    try:
        # TelegramFootballBot instance oluştur
        bot = TelegramFootballBot()
        
        print("✅ Bot instance oluşturuldu")
        print("📱 Telegram komutları hazır:")
        print("   /start - Bot'u başlat")
        print("   /epl - Premier League")
        print("   /laliga - La Liga")
        print("   /bundesliga - Bundesliga")
        print("   /seriea - Serie A")
        print("   /superlig - Süper Lig")
        print("   /ligue1 - Ligue 1")
        print("   /all - Tüm liglerden bugünkü maçlar")
        print("   /help - Yardım")
        
        print("\n🚀 Bot çalışmaya başlıyor...")
        print("=" * 50)
        
        # Bot'u çalıştır (blocking call)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ Bot kapatılıyor (Ctrl+C)")
        
    except Exception as e:
        print(f"\n❌ Bot başlatma hatası:")
        print(f"   Hata: {str(e)}")
        print(f"   Tip: {type(e).__name__}")
        
        # Hata debug bilgileri
        print("\n🔧 DEBUG BİLGİLERİ:")
        print("   1. Telegram token doğru mu?")
        print("   2. Chat ID doğru mu?")
        print("   3. Bot @BotFather'da aktif mi?")
        print("   4. Internet bağlantısı var mı?")
        
        if env_type == 'railway':
            print("\n🚂 Railway Debug:")
            print("   1. Logs sekmesinden detaylı hata loglarını kontrol et")
            print("   2. Environment variables doğru ayarlandı mı?")
            print("   3. Deployment successful oldu mu?")
        
        exit(1)

if __name__ == "__main__":
    main()