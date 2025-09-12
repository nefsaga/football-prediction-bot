import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import config
from real_data_collector import RealDataCollector
from advanced_predictor import AdvancedPredictor
from odds_analyzer import OddsAnalyzer
from sportsdb_fetcher import SportsDBFetcher

class TelegramFootballBot:
    def __init__(self):
        self.predictor = AdvancedPredictor()
        self.odds_analyzer = OddsAnalyzer()
        self.fixture_fetcher = SportsDBFetcher()
        
        self.available_leagues = {
            'E0': 'Premier League',
            'T1': 'Süper Lig',
            'D1': 'Bundesliga',
            'D2': '2.Bundesliga',
            'SP1': 'La Liga',
            'SP2': 'La Liga 2',
            'I1': 'Serie A',
            'I2': 'Serie B',
            'F1': 'Ligue 1',
            'B1': 'Jupiler Pro League',
            'P1': 'Primeira Liga'
        }
    
    def get_confidence_emoji(self, percentage):
        if percentage >= 80: return "🔥"
        elif percentage >= 70: return "⭐"
        elif percentage >= 60: return "✅"
        elif percentage >= 50: return "⚠️"
        else: return "❌"
    
    def format_prediction_with_confidence(self, value):
        emoji = self.get_confidence_emoji(value)
        return f"%{value} {emoji}"
    
    def format_h2h_record(self, wins, draws, losses):
        if wins + draws + losses == 0:
            return "Veri yok"
        return f"{wins}G-{draws}B-{losses}M"
    
    async def send_league_predictions(self, update: Update, league_code: str):
        """Belirli lig için tahminler gönder"""
        try:
            collector = RealDataCollector(league_code)
            
            # Gerçek fixture'ları SportsDB'den al
            fixtures = self.fixture_fetcher.get_today_fixtures(league_code)
            
            if not fixtures:
                no_match_msg = f"""❌ {collector.league_config['name']} - Bugün Maç Yok

📅 {datetime.now().strftime('%A, %d %B %Y')}

Bu ligde bugün maç bulunmuyor.
Genellikle maçlar:
- Cumartesi-Pazar (hafta sonu)
- Çarşamba-Perşembe (Avrupa kupası günleri)

📋 /leagues - Diğer ligleri kontrol et
🏆 /help - Yardım menüsü"""
                
                await update.message.reply_text(no_match_msg)
                return
            
            # Lig başlığı
            header = f"""🏆 {collector.league_config['name']} TAHMİNLERİ
🌍 {collector.league_config['country']}
📅 {datetime.now().strftime('%d/%m/%Y')}
🎯 {len(fixtures)} Maç Analizi

════════════════════════════════════════"""
            
            await update.message.reply_text(header)
            
            for i, fixture in enumerate(fixtures, 1):
                home = fixture['home_team']
                away = fixture['away_team']
                match_date = fixture['date']
                match_time = fixture['time']
                
                # Loading mesajı
                loading_msg = f"🔍 {i}/{len(fixtures)} - {home} vs {away} analizi..."
                loading_message = await update.message.reply_text(loading_msg)
                
                try:
                    # Analiz
                    analysis = collector.get_match_analysis(home, away)
                    match_outcome = self.predictor.predict_match_outcome(home, away)
                    goal_markets = self.predictor.predict_goal_markets(home, away)
                    btts_prediction = self.predictor.predict_btts(home, away)
                    corners_cards = self.predictor.predict_corners_cards_advanced(home, away)
                    
                    # Oran analizi
                    all_predictions = {
                        'match_outcome': match_outcome,
                        'goal_markets': goal_markets,
                        'btts': btts_prediction
                    }
                    odds_analysis = self.odds_analyzer.comprehensive_odds_analysis(home, away, all_predictions)
                    
                    h2h_data = analysis['head_to_head']
                    home_xg, away_xg = match_outcome['expected_goals']
                    home_momentum, away_momentum = match_outcome['momentum']
                    
                    # Loading mesajını sil
                    await loading_message.delete()
                    
                    message = f"""⚽ {home} vs {away}
📅 {match_date} | 🕐 {match_time}

📊 EXPECTED GOALS & MOMENTUM
xG: {home} {home_xg} - {away_xg} {away}
📈 Momentum: {home} {home_momentum:.2f} | {away} {away_momentum:.2f}

🏆 SONUÇ TAHMİNİ
- 90dk: {home} {self.format_prediction_with_confidence(match_outcome['full_time'][0])} | X {self.format_prediction_with_confidence(match_outcome['full_time'][1])} | {away} {self.format_prediction_with_confidence(match_outcome['full_time'][2])}
- 45dk: {home} {self.format_prediction_with_confidence(match_outcome['half_time'][0])} | X {self.format_prediction_with_confidence(match_outcome['half_time'][1])} | {away} {self.format_prediction_with_confidence(match_outcome['half_time'][2])}

🆚 HEAD-TO-HEAD ANALİZİ
- Son 5 maç: {self.format_h2h_record(h2h_data.get('general_h2h_wins', 0), h2h_data.get('general_h2h_draws', 0), h2h_data.get('general_h2h_losses', 0))}
- {home} evinde: {self.format_h2h_record(h2h_data.get('home_h2h_wins', 0), h2h_data.get('home_h2h_draws', 0), h2h_data.get('home_h2h_losses', 0))}

⚽ GOL TAHMİNLERİ
🎯 Total: O1.5 {self.format_prediction_with_confidence(goal_markets['total']['over_1.5'])} | O2.5 {self.format_prediction_with_confidence(goal_markets['total']['over_2.5'])} | O3.5 {self.format_prediction_with_confidence(goal_markets['total']['over_3.5'])}
🏠 {home}: O0.5 {self.format_prediction_with_confidence(goal_markets['home_team']['over_0.5'])} | O1.5 {self.format_prediction_with_confidence(goal_markets['home_team']['over_1.5'])} | O2.5 {self.format_prediction_with_confidence(goal_markets['home_team']['over_2.5'])}
✈️ {away}: O0.5 {self.format_prediction_with_confidence(goal_markets['away_team']['over_0.5'])} | O1.5 {self.format_prediction_with_confidence(goal_markets['away_team']['over_1.5'])} | O2.5 {self.format_prediction_with_confidence(goal_markets['away_team']['over_2.5'])}
🎲 BTTS: Evet {self.format_prediction_with_confidence(btts_prediction[0])} | Hayır {self.format_prediction_with_confidence(btts_prediction[1])}

🚩 KORNERLER
🎯 Total: O8.5 {self.format_prediction_with_confidence(corners_cards['corners']['total']['over_8.5'])} | O10.5 {self.format_prediction_with_confidence(corners_cards['corners']['total']['over_10.5'])} | O12.5 {self.format_prediction_with_confidence(corners_cards['corners']['total']['over_12.5'])}

🟨 KARTLAR
🎯 Total: O3.5 {self.format_prediction_with_confidence(corners_cards['cards']['total']['over_3.5'])} | O4.5 {self.format_prediction_with_confidence(corners_cards['cards']['total']['over_4.5'])} | O5.5 {self.format_prediction_with_confidence(corners_cards['cards']['total']['over_5.5'])}

💰 ORAN ANALİZİ"""

                    # Value bet önerileri
                    if odds_analysis['value_bets']:
                        message += "\n🎯 VALUE BET FIRSATLARI:"
                        for bet in odds_analysis['value_bets']:
                            if bet['value'] > 5:
                                message += f"\n• {bet['market']}: +%{bet['value']} value @ {bet['best_odds']}"
                    else:
                        message += "\n⚠️ Şu anda güçlü value bet yok"

                    message += f"""

🤖 Model: Advanced Multi-League Prediction System
📊 Veri: 3 sezon + 4 sezon H2H | API: TheSportsDB
🎯 Güven: 🔥 Çok Yüksek | ⭐ Yüksek | ✅ İyi | ⚠️ Orta

════════════════════════════════════════"""
                    
                    await update.message.reply_text(message)
                    
                except Exception as match_error:
                    await loading_message.delete()
                    error_msg = f"❌ {home} vs {away} analizi başarısız: {str(match_error)}"
                    await update.message.reply_text(error_msg)
                
                # Maçlar arası kısa bekle
                if i < len(fixtures):
                    await asyncio.sleep(2)
                    
        except Exception as e:
            await update.message.reply_text(f"❌ Lig analizi hatası: {str(e)}")

    # Komut handlers
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome = """🤖 Football Prediction Bot'a Hoş Geldiniz!

📊 11 Lig | Real-Time Fixtures | Advanced Analytics

🏆 ANA LİGLER:
/epl - Premier League 🇬🇧
/laliga - La Liga 🇪🇸
/bundesliga - Bundesliga 🇩🇪
/seriea - Serie A 🇮🇹
/superlig - Süper Lig 🇹🇷
/ligue1 - Ligue 1 🇫🇷

⚽ İKİNCİ LİGLER:
/laliga2 - La Liga 2 🇪🇸
/bundesliga2 - 2.Bundesliga 🇩🇪
/serieb - Serie B 🇮🇹

🌍 DİĞER LİGLER:
/jupiler - Jupiler Pro League 🇧🇪
/primeira - Primeira Liga 🇵🇹

📋 /leagues - Tüm ligler | ❓ /help - Yardım

⚠️ Sorumlu bahis: Sadece kaybetmeyi göze alabileceğiniz miktarlarla bahis yapın."""
        
        await update.message.reply_text(welcome)

    # Ana Ligler
    async def cmd_epl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'E0')

    async def cmd_laliga(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'SP1')

    async def cmd_bundesliga(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'D1')

    async def cmd_seriea(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'I1')

    async def cmd_superlig(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'T1')

    async def cmd_ligue1(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'F1')

    # İkinci Ligler
    async def cmd_laliga2(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'SP2')

    async def cmd_bundesliga2(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'D2')

    async def cmd_serieb(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'I2')

    # Diğer Ligler
    async def cmd_jupiler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'B1')

    async def cmd_primeira(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.send_league_predictions(update, 'P1')

    async def cmd_leagues(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        leagues_text = f"""🏆 MEVCUT LİGLER ({len(self.available_leagues)} adet)

🇬🇧 ENGLAND:
/epl - Premier League

🇪🇸 SPAIN:
/laliga - La Liga
/laliga2 - La Liga 2

🇩🇪 GERMANY:
/bundesliga - Bundesliga
/bundesliga2 - 2.Bundesliga

🇮🇹 ITALY:
/seriea - Serie A
/serieb - Serie B

🇫🇷 FRANCE:
/ligue1 - Ligue 1

🇹🇷 TURKEY:
/superlig - Süper Lig

🇧🇪 BELGIUM:
/jupiler - Jupiler Pro League

🇵🇹 PORTUGAL:
/primeira - Primeira Liga

📊 Real-time fixtures from TheSportsDB API
🎯 Advanced prediction algorithms
💰 Value bet analysis

📋 /help - Detaylı sistem bilgisi"""
        
        await update.message.reply_text(leagues_text)

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""🤖 Football Prediction Bot - Sistem Rehberi

📊 SİSTEM ÖZELLİKLERİ:
- 11 profesyonel lig
- Real-time fixture entegrasyonu (TheSportsDB)
- 3 sezon veri analizi (2023-2026)
- 4 sezon H2H karşılaştırma
- Advanced Poisson + Form algoritması
- Expected Goals hesaplaması
- Momentum analizi

🎯 TAHMİN TÜRLERİ:
- 1X2 (90dk + 45dk)
- Over/Under (Total + Takım bazlı)
- Both Teams To Score
- Korner pazarları (8.5, 10.5, 12.5)
- Kart pazarları (3.5, 4.5, 5.5)
- Value bet fırsatları

📱 KOMUT LİSTESİ:
Ana ligler: /epl /laliga /bundesliga /seriea /superlig /ligue1
İkinci ligler: /laliga2 /bundesliga2 /serieb
Diğer: /jupiler /primeira
Sistem: /leagues /help

📊 GÜVEN SEVİYELERİ:
🔥 Çok Yüksek (80%+) - En güvenli tahminler
⭐ Yüksek (70%+) - İyi güven seviyesi
✅ İyi (60%+) - Orta-üst güven
⚠️ Orta (50%+) - Dikkatli yaklaşım

💰 VALUE BET SİSTEMİ:
Bot %5'ten yüksek value tespit ettiğinde önerir.
Value bet = (Tahmin olasılığı / Oran) - 1

🔧 VERİ KAYNAKLARI:
- Maç verileri: Football-data.co.uk
- Fixture'lar: TheSportsDB API
- H2H analizi: 4 sezon geçmiş
- Form analizi: Son 10 maç

⚠️ ÖNEMLİ UYARI:
Bu sistem analiz aracıdır, %100 garanti vermez.
- Bahis sonuçları kesin değildir
- Sadece kaybetmeyi göze alabileceğiniz miktarlarla bahis yapın
- Bahis bağımlılığına karşı dikkatli olun
- Profesyonel yardım almaktan çekinmeyin

🏆 Sistem sürekli geliştirilmektedir.
Geri bildirimleriniz değerlidir."""
        
        await update.message.reply_text(help_text)

    async def cmd_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bugün maçı olan tüm liglerin tahminleri"""
        await update.message.reply_text("🔍 Tüm ligler kontrol ediliyor...")
        
        predictions_sent = 0
        for league_code, league_name in self.available_leagues.items():
            fixtures = self.fixture_fetcher.get_today_fixtures(league_code)
            if fixtures:
                await self.send_league_predictions(update, league_code)
                predictions_sent += 1
                await asyncio.sleep(3)  # Ligler arası bekle
        
        if predictions_sent == 0:
            await update.message.reply_text("📅 Bugün hiçbir ligde maç yok.")
        else:
            await update.message.reply_text(f"✅ {predictions_sent} ligden tahminler tamamlandı!")

    def run(self):
        """Bot'u başlat"""
        application = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # Ana Lig Komutları
        application.add_handler(CommandHandler("start", self.cmd_start))
        application.add_handler(CommandHandler("epl", self.cmd_epl))
        application.add_handler(CommandHandler("laliga", self.cmd_laliga))
        application.add_handler(CommandHandler("bundesliga", self.cmd_bundesliga))
        application.add_handler(CommandHandler("seriea", self.cmd_seriea))
        application.add_handler(CommandHandler("superlig", self.cmd_superlig))
        application.add_handler(CommandHandler("ligue1", self.cmd_ligue1))
        
        # İkinci Lig Komutları
        application.add_handler(CommandHandler("laliga2", self.cmd_laliga2))
        application.add_handler(CommandHandler("bundesliga2", self.cmd_bundesliga2))
        application.add_handler(CommandHandler("serieb", self.cmd_serieb))
        
        # Diğer Lig Komutları
        application.add_handler(CommandHandler("jupiler", self.cmd_jupiler))
        application.add_handler(CommandHandler("primeira", self.cmd_primeira))
        
        # Özel Komutlar
        application.add_handler(CommandHandler("all", self.cmd_all))
        
        # Sistem Komutları
        application.add_handler(CommandHandler("leagues", self.cmd_leagues))
        application.add_handler(CommandHandler("help", self.cmd_help))
        
        print("🤖 Football Prediction Bot başlatılıyor...")
        print("📱 Real-time fixture entegrasyonu aktif")
        print("🏆 11 lig, gerçek maç verileriyle hazır")
        print("🎯 Telegram'dan /start yazarak kullanmaya başlayabilirsiniz")
        print("\n📋 Mevcut komutlar:")
        print("   Ana: /epl /laliga /bundesliga /seriea /superlig /ligue1")
        print("   İkinci: /laliga2 /bundesliga2 /serieb")  
        print("   Diğer: /jupiler /primeira")
        print("   Özel: /all (tüm liglerden bugünkü maçlar)")
        print("   Sistem: /leagues /help")
        
        # Bot'u çalıştır
        application.run_polling()

if __name__ == "__main__":
    bot = TelegramFootballBot()
    bot.run()