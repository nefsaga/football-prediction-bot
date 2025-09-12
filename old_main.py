# old_main.py - Eski main dosyasını yedek olarak sakla
import asyncio
from telegram import Bot
from datetime import datetime
import config
from real_data_collector import RealDataCollector
from advanced_predictor import AdvancedPredictor
from odds_analyzer import OddsAnalyzer

# ... [eski main.py içeriği burada kalır] ...
import asyncio
from telegram import Bot
from datetime import datetime
import config
from real_data_collector import RealDataCollector
from advanced_predictor import AdvancedPredictor
from odds_analyzer import OddsAnalyzer

class FootballBot:
    def __init__(self, league_code='E0'):
        self.bot = Bot(token=config.TELEGRAM_TOKEN)
        self.league_code = league_code
        self.collector = RealDataCollector(league_code)
        self.predictor = AdvancedPredictor()
        self.odds_analyzer = OddsAnalyzer()
        
        # Mevcut ligler
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
        """Güven seviyesi emojisi"""
        if percentage >= 80:
            return "🔥"
        elif percentage >= 70:
            return "⭐"
        elif percentage >= 60:
            return "✅"
        elif percentage >= 50:
            return "⚠️"
        else:
            return "❌"
    
    def format_prediction_with_confidence(self, value):
        """Tahmin + güven göstergesi"""
        emoji = self.get_confidence_emoji(value)
        return f"%{value} {emoji}"
    
    def format_h2h_record(self, wins, draws, losses):
        """H2H rekor formatı"""
        if wins + draws + losses == 0:
            return "Veri yok"
        return f"{wins}G-{draws}B-{losses}M"
    
    async def send_league_predictions(self, league_code=None):
        """Belirli lig için tahminler"""
        if league_code and league_code in self.available_leagues:
            self.league_code = league_code
            self.collector = RealDataCollector(league_code)
        
        fixtures = self.collector.fetch_fixtures()
        
        if not fixtures:
            await self.bot.send_message(
                chat_id=config.CHAT_ID,
                text=f"⚽ Bugün {self.collector.league_config['name']} maçı bulunamadı."
            )
            return
        
        # Lig başlığı
        league_header = f"""
🏆 {self.collector.league_config['name']} TAHMİNLERİ
🌍 {self.collector.league_config['country']}
📅 {datetime.now().strftime('%d/%m/%Y')}

════════════════════════════════════════
"""
        await self.bot.send_message(chat_id=config.CHAT_ID, text=league_header)
        
        for fixture in fixtures:
            home = fixture['home_team']
            away = fixture['away_team']
            time = fixture['time']
            league = fixture['league']
            
            # Analiz (tek seferlik veri çekme)
            print(f"🔍 {league}: {home} vs {away} analizi başlıyor...")
            analysis = self.collector.get_match_analysis(home, away)
            
            # Tahminleri al
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
            
            # Verileri çıkar
            h2h_data = analysis['head_to_head']
            home_xg, away_xg = match_outcome['expected_goals']
            home_momentum, away_momentum = match_outcome['momentum']
            
            message = f"""
⚽ {home} vs {away} | 🕐 {time}

📊 EXPECTED GOALS & MOMENTUM
xG: {home} {home_xg} - {away_xg} {away}
Momentum: {home} {home_momentum:.2f} | {away} {away_momentum:.2f}

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

🤖 Model: Multi-League Advanced Prediction System
📊 Veri: 3 sezon + 4 sezon H2H
🎯 Güven: 🔥 Çok Yüksek | ⭐ Yüksek | ✅ İyi | ⚠️ Orta

════════════════════════════════════════
"""
            
            await self.bot.send_message(chat_id=config.CHAT_ID, text=message)
            print(f"✅ {league} tahmini gönderildi!")

    async def send_all_leagues_predictions(self):
        """Tüm mevcut liglerin tahminleri"""
        total_predictions = 0
        
        header = f"""
🌍 GÜNÜN TÜM LİG TAHMİNLERİ
📅 {datetime.now().strftime('%d/%m/%Y')}
🏆 {len(self.available_leagues)} Lig Aktif

════════════════════════════════════════
"""
        await self.bot.send_message(chat_id=config.CHAT_ID, text=header)
        
        for league_code, league_name in self.available_leagues.items():
            try:
                print(f"📊 {league_name} tahminleri hazırlanıyor...")
                await self.send_league_predictions(league_code)
                total_predictions += 1
                
                # Ligler arası kısa bekle
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ {league_name} hatası: {e}")
                continue
        
        footer = f"""
📊 GÜNLÜK ÖZET TAMAMLANDI
✅ {total_predictions} lig analiz edildi
🎯 Toplam maç sayısı: {total_predictions * 2} (ortalama)

⚠️ Bahis Uyarısı: Bu tahminler analiz aracıdır, %100 garanti değildir.
Sadece kaybetmeyi göze alabileceğiniz miktarlarla bahis yapın.
"""
        await self.bot.send_message(chat_id=config.CHAT_ID, text=footer)

    async def send_available_leagues(self):
        """Mevcut ligleri listele"""
        leagues_text = f"""
🏆 MEVCUT LİGLER ({len(self.available_leagues)} adet)

🇬🇧 İNGİLTERE:
- Premier League (E0)

🇹🇷 TÜRKİYE:
- Süper Lig (T1)

🇩🇪 ALMANYA:
- Bundesliga (D1)
- 2.Bundesliga (D2)

🇪🇸 İSPANYA:
- La Liga (SP1)
- La Liga 2 (SP2)

🇮🇹 İTALYA:
- Serie A (I1)
- Serie B (I2)

🇫🇷 FRANSA:
- Ligue 1 (F1)

🇧🇪 BELÇİKA:
- Jupiler Pro League (B1)

🇵🇹 PORTEKİZ:
- Primeira Liga (P1)

🎮 KOMUTLAR (Yakında):
/all - Tüm ligler
/epl - Premier League
/laliga - La Liga
/bundesliga - Bundesliga
/seriea - Serie A
/superlig - Süper Lig
"""
        await self.bot.send_message(chat_id=config.CHAT_ID, text=leagues_text)

    async def send_help(self):
        """Yardım menüsü"""
        help_text = f"""
🤖 Football Prediction Bot - Multi-League Pro

📊 SİSTEM KAPSAMI:
- {len(self.available_leagues)} profesyonel lig
- 3 sezon veri analizi (2023-2026)
- 4 sezon H2H karşılaştırma
- Advanced Poisson + Form algoritması

🎯 TAHMİN TÜRLERİ:
- 1X2 (90dk + 45dk)
- Over/Under (Total + Takım bazlı)
- Both Teams To Score
- Korner pazarları
- Kart pazarları
- Expected Goals
- Value bet fırsatları

💰 ORAN ANALİZİ:
- Real-time oran karşılaştırma
- Value bet tespiti
- Sharp money sinyalleri
- En iyi oranlar

🔧 KULLANIM:
Bu sistem analiz aracıdır. Bahis yaparken dikkatli olun.
"""
        await self.bot.send_message(chat_id=config.CHAT_ID, text=help_text)

async def main():
    """Test - farklı ligleri dene"""
    bot = FootballBot()
    
    # Tek lig test
    print("=== TEK LİG TESTİ ===")
    await bot.send_league_predictions('SP1')  # La Liga
    
    # Birden fazla lig test (istersen)
    # print("=== ÇOK LİG TESTİ ===")
    # await bot.send_all_leagues_predictions()

if __name__ == "__main__":
    asyncio.run(main())
# Bu dosya artık kullanılmıyor, sadece yedek amaçlı