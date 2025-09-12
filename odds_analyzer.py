import requests
from datetime import datetime
import json

class OddsAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
    def get_mock_odds(self, home_team, away_team):
        """Mock oran verisi (gerçek API entegrasyonu için temel)"""
        # Gerçek hayatta burası betting API'lerinden gelecek
        mock_odds = {
            'bookmakers': {
                'bet365': {
                    'home_win': 1.85,
                    'draw': 3.60,
                    'away_win': 4.20,
                    'over_2.5': 1.90,
                    'under_2.5': 1.95,
                    'btts_yes': 1.75,
                    'btts_no': 2.10
                },
                'pinnacle': {
                    'home_win': 1.88,
                    'draw': 3.65,
                    'away_win': 4.15,
                    'over_2.5': 1.92,
                    'under_2.5': 1.93,
                    'btts_yes': 1.78,
                    'btts_no': 2.07
                },
                'betfair': {
                    'home_win': 1.87,
                    'draw': 3.70,
                    'away_win': 4.10,
                    'over_2.5': 1.95,
                    'under_2.5': 1.90,
                    'btts_yes': 1.80,
                    'btts_no': 2.05
                }
            },
            'movements': {
                'home_win': {'24h_ago': 1.90, 'current': 1.85, 'change': -2.6},
                'over_2.5': {'24h_ago': 1.85, 'current': 1.90, 'change': +2.7},
                'btts_yes': {'24h_ago': 1.70, 'current': 1.75, 'change': +2.9}
            }
        }
        
        return mock_odds
    
    def odds_to_probability(self, odds):
        """Oranları olasılığa çevir"""
        return round((1 / odds) * 100, 1)
    
    def calculate_value_bet(self, my_probability, bookmaker_odds):
        """Value bet hesaplama"""
        bookmaker_probability = self.odds_to_probability(bookmaker_odds)
        value = my_probability - bookmaker_probability
        
        if value > 5:  # %5+ fark
            return {
                'has_value': True,
                'value_percentage': round(value, 1),
                'confidence': 'High' if value > 10 else 'Medium'
            }
        
        return {
            'has_value': False,
            'value_percentage': round(value, 1),
            'confidence': 'Low'
        }
    
    def find_best_odds(self, odds_data, market):
        """En iyi oranı bul"""
        best_odds = 0
        best_bookmaker = ''
        
        for bookmaker, odds in odds_data['bookmakers'].items():
            if market in odds and odds[market] > best_odds:
                best_odds = odds[market]
                best_bookmaker = bookmaker
        
        return {
            'odds': best_odds,
            'bookmaker': best_bookmaker,
            'profit_margin': round(((best_odds - min([odds[market] for odds in odds_data['bookmakers'].values() if market in odds])) / best_odds) * 100, 1)
        }
    
    def analyze_odds_movement(self, odds_data, market):
        """Oran hareketi analizi"""
        if market not in odds_data['movements']:
            return None
            
        movement = odds_data['movements'][market]
        change_pct = movement['change']
        
        analysis = {
            'direction': 'rising' if change_pct > 0 else 'falling',
            'change_percentage': abs(change_pct),
            'significance': 'High' if abs(change_pct) > 5 else 'Medium' if abs(change_pct) > 2 else 'Low'
        }
        
        if analysis['direction'] == 'falling' and analysis['significance'] == 'High':
            analysis['signal'] = 'Sharp Money Detected'
        elif analysis['direction'] == 'rising' and analysis['significance'] == 'High':
            analysis['signal'] = 'Public Money Flow'
        else:
            analysis['signal'] = 'Normal Movement'
            
        return analysis
    
    def comprehensive_odds_analysis(self, home_team, away_team, my_predictions):
        """Kapsamlı oran analizi"""
        odds_data = self.get_mock_odds(home_team, away_team)
        
        analysis = {
            'match': f"{home_team} vs {away_team}",
            'value_bets': [],
            'best_odds': {},
            'movements': {},
            'recommendations': []
        }
        
        # Tahminlerimle karşılaştır
        markets_to_analyze = {
            'home_win': my_predictions['match_outcome']['full_time'][0],
            'over_2.5': my_predictions['goal_markets']['total']['over_2.5'],
            'btts_yes': my_predictions['btts'][0]
        }
        
        for market, my_prob in markets_to_analyze.items():
            # En iyi oranları bul
            best_odds_info = self.find_best_odds(odds_data, market)
            analysis['best_odds'][market] = best_odds_info
            
            # Value bet kontrolü
            value_analysis = self.calculate_value_bet(my_prob, best_odds_info['odds'])
            
            if value_analysis['has_value']:
                analysis['value_bets'].append({
                    'market': market,
                    'my_probability': my_prob,
                    'best_odds': best_odds_info['odds'],
                    'bookmaker': best_odds_info['bookmaker'],
                    'value': value_analysis['value_percentage'],
                    'confidence': value_analysis['confidence']
                })
            
            # Oran hareketi analizi
            movement_analysis = self.analyze_odds_movement(odds_data, market)
            if movement_analysis:
                analysis['movements'][market] = movement_analysis
        
        # Öneriler
        if len(analysis['value_bets']) > 0:
            high_value_bets = [bet for bet in analysis['value_bets'] if bet['confidence'] == 'High']
            if high_value_bets:
                analysis['recommendations'].append("Strong value bets detected - consider these markets")
            else:
                analysis['recommendations'].append("Moderate value opportunities available")
        else:
            analysis['recommendations'].append("No significant value detected - wait for better opportunities")
        
        # Sharp money sinyalleri
        sharp_signals = [market for market, movement in analysis['movements'].items() 
                        if movement.get('signal') == 'Sharp Money Detected']
        if sharp_signals:
            analysis['recommendations'].append(f"Sharp money detected on: {', '.join(sharp_signals)}")
        
        return analysis

# Test
if __name__ == "__main__":
    analyzer = OddsAnalyzer()
    
    # Mock predictions
    mock_predictions = {
        'match_outcome': {'full_time': (65, 20, 15)},
        'goal_markets': {'total': {'over_2.5': 72}},
        'btts': (58, 42)
    }
    
    analysis = analyzer.comprehensive_odds_analysis("Arsenal", "Manchester City", mock_predictions)
    
    print("Oran Analizi:")
    print(f"Value Bets: {len(analysis['value_bets'])}")
    if analysis['value_bets']:
        for bet in analysis['value_bets']:
            print(f"  {bet['market']}: %{bet['value']} value ({bet['confidence']})")
    
    print(f"Öneriler: {analysis['recommendations']}")