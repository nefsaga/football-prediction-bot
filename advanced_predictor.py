import math
import numpy as np
from real_data_collector import RealDataCollector

class AdvancedPredictor:
    def __init__(self):
        self.collector = RealDataCollector()
    
    def calculate_expected_goals(self, home_team, away_team):
        """Gelişmiş Expected Goals hesaplaması"""
        # Kapsamlı maç analizi al
        analysis = self.collector.get_match_analysis(home_team, away_team)
        
        home_data = analysis['home_team']
        away_data = analysis['away_team']
        h2h_data = analysis['head_to_head']
        
        # Ev sahibi expected goals
        # 1. Sezon ortalamaları (ağırlık: 40%)
        home_season_goals = (
            home_data['season_current'].get('season_home_goals_avg', 1.5) * 0.7 +
            home_data['season_previous'].get('season_home_goals_avg', 1.5) * 0.3
        )
        away_season_conceded = (
            away_data['season_current'].get('season_away_conceded_avg', 1.2) * 0.7 +
            away_data['season_previous'].get('season_away_conceded_avg', 1.2) * 0.3
        )
        
        # 2. Son form (ağırlık: 35%)
        home_recent_goals = home_data['form'].get('home_goals_avg', 1.5)
        away_recent_conceded = away_data['form'].get('away_conceded_avg', 1.2)
        
        # 3. H2H analizi (ağırlık: 25%)
        h2h_home_goals = h2h_data.get('home_h2h_goals_avg', 1.5)
        if h2h_data.get('home_h2h_games', 0) < 2:
            # Az H2H verisi varsa ağırlığı azalt
            h2h_weight = 0.1
            form_weight = 0.5
            season_weight = 0.4
        else:
            h2h_weight = 0.25
            form_weight = 0.35
            season_weight = 0.4
        
        # Ev sahibi xG
        home_attack_strength = (
            home_season_goals * season_weight +
            home_recent_goals * form_weight +
            h2h_home_goals * h2h_weight
        )
        
        away_defense_weakness = (
            away_season_conceded * season_weight +
            away_recent_conceded * form_weight +
            h2h_data.get('home_h2h_conceded_avg', 1.2) * h2h_weight
        )
        
        home_xg = (home_attack_strength + away_defense_weakness) / 2
        
        # Deplasman expected goals (benzer hesaplama)
        away_season_goals = (
            away_data['season_current'].get('season_away_goals_avg', 1.2) * 0.7 +
            away_data['season_previous'].get('season_away_goals_avg', 1.2) * 0.3
        )
        home_season_conceded = (
            home_data['season_current'].get('season_home_conceded_avg', 1.1) * 0.7 +
            home_data['season_previous'].get('season_home_conceded_avg', 1.1) * 0.3
        )
        
        away_recent_goals = away_data['form'].get('away_goals_avg', 1.2)
        home_recent_conceded = home_data['form'].get('home_conceded_avg', 1.1)
        
        h2h_away_goals = h2h_data.get('away_h2h_goals_avg', 1.2)
        
        away_attack_strength = (
            away_season_goals * season_weight +
            away_recent_goals * form_weight +
            h2h_away_goals * h2h_weight
        )
        
        home_defense_weakness = (
            home_season_conceded * season_weight +
            home_recent_conceded * form_weight +
            h2h_data.get('away_h2h_conceded_avg', 1.1) * h2h_weight
        )
        
        away_xg = (away_attack_strength + home_defense_weakness) / 2
        
        return round(home_xg, 2), round(away_xg, 2)
    
    def calculate_form_momentum(self, team_data):
        """Form momentum hesaplama"""
        recent_form = team_data['form'].get('overall_form_avg', 1.5)
        home_form = team_data['form'].get('home_form_avg', 1.5)
        away_form = team_data['form'].get('away_form_avg', 1.5)
        
        # Momentum faktörü (0.8 - 1.2 arası)
        if recent_form >= 2.5:
            momentum = 1.15
        elif recent_form >= 2.0:
            momentum = 1.08
        elif recent_form >= 1.5:
            momentum = 1.0
        elif recent_form >= 1.0:
            momentum = 0.92
        else:
            momentum = 0.85
            
        return momentum
    
    def poisson_probability(self, expected, actual):
        """Poisson dağılımı olasılık hesaplama"""
        if expected <= 0:
            expected = 0.1
        try:
            return (math.exp(-expected) * (expected ** actual)) / math.factorial(actual)
        except:
            return 0.01
    
    def predict_match_outcome(self, home_team, away_team):
        """Ana tahmin fonksiyonu"""
        # Expected goals hesapla
        home_xg, away_xg = self.calculate_expected_goals(home_team, away_team)
        
        # Analiz verilerini al
        analysis = self.collector.get_match_analysis(home_team, away_team)
        
        # Momentum faktörleri
        home_momentum = self.calculate_form_momentum(analysis['home_team'])
        away_momentum = self.calculate_form_momentum(analysis['away_team'])
        
        # Momentum ile ayarlanmış xG
        adjusted_home_xg = home_xg * home_momentum
        adjusted_away_xg = away_xg * away_momentum
        
        # Poisson ile skor olasılıkları
        match_probabilities = {}
        total_prob = 0
        
        for home_goals in range(0, 6):
            for away_goals in range(0, 6):
                home_prob = self.poisson_probability(adjusted_home_xg, home_goals)
                away_prob = self.poisson_probability(adjusted_away_xg, away_goals)
                match_prob = home_prob * away_prob
                
                match_probabilities[(home_goals, away_goals)] = match_prob
                total_prob += match_prob
        
        # Sonuç olasılıkları
        home_win_prob = sum([prob for (h, a), prob in match_probabilities.items() if h > a])
        draw_prob = sum([prob for (h, a), prob in match_probabilities.items() if h == a])
        away_win_prob = sum([prob for (h, a), prob in match_probabilities.items() if h < a])
        
        # Normalize
        total = home_win_prob + draw_prob + away_win_prob
        home_win_pct = int((home_win_prob / total) * 100)
        draw_pct = int((draw_prob / total) * 100)
        away_win_pct = 100 - home_win_pct - draw_pct
        
        # İlk yarı (daha konservatif)
        ht_home = int(home_win_pct * 0.65)
        ht_draw = int(draw_pct * 1.4)
        ht_away = 100 - ht_home - ht_draw
        
        return {
            'full_time': (home_win_pct, draw_pct, away_win_pct),
            'half_time': (ht_home, ht_draw, ht_away),
            'expected_goals': (adjusted_home_xg, adjusted_away_xg),
            'momentum': (home_momentum, away_momentum)
        }
    
    def predict_goal_markets(self, home_team, away_team):
        """Gol pazarları tahmini"""
        home_xg, away_xg = self.calculate_expected_goals(home_team, away_team)
        total_xg = home_xg + away_xg
        
        # Total goals
        total_predictions = {
            'over_1.5': int(min(95, 100 - (self.poisson_probability(total_xg, 0) + self.poisson_probability(total_xg, 1)) * 100)),
            'over_2.5': int(min(90, 100 - sum([self.poisson_probability(total_xg, i) for i in range(3)]) * 100)),
            'over_3.5': int(min(85, 100 - sum([self.poisson_probability(total_xg, i) for i in range(4)]) * 100))
        }
        
        # Home team goals
        home_predictions = {
            'over_0.5': int(min(95, (1 - self.poisson_probability(home_xg, 0)) * 100)),
            'over_1.5': int(min(90, (1 - self.poisson_probability(home_xg, 0) - self.poisson_probability(home_xg, 1)) * 100)),
            'over_2.5': int(min(85, (1 - sum([self.poisson_probability(home_xg, i) for i in range(3)])) * 100))
        }
        
        # Away team goals
        away_predictions = {
            'over_0.5': int(min(90, (1 - self.poisson_probability(away_xg, 0)) * 100)),
            'over_1.5': int(min(85, (1 - self.poisson_probability(away_xg, 0) - self.poisson_probability(away_xg, 1)) * 100)),
            'over_2.5': int(min(80, (1 - sum([self.poisson_probability(away_xg, i) for i in range(3)])) * 100))
        }
        
        return {
            'total': total_predictions,
            'home_team': home_predictions,
            'away_team': away_predictions
        }
    
    def predict_btts(self, home_team, away_team):
        """BTTS tahmini"""
        home_xg, away_xg = self.calculate_expected_goals(home_team, away_team)
        
        home_scores_prob = 1 - self.poisson_probability(home_xg, 0)
        away_scores_prob = 1 - self.poisson_probability(away_xg, 0)
        
        btts_prob = int(home_scores_prob * away_scores_prob * 100)
        btts_prob = min(85, max(25, btts_prob))
        
        return btts_prob, 100 - btts_prob
    
    def predict_corners_cards_advanced(self, home_team, away_team):
        """Gelişmiş korner/kart tahmini"""
        analysis = self.collector.get_match_analysis(home_team, away_team)
        
        home_data = analysis['home_team']
        away_data = analysis['away_team']
        
        # Korner tahmini (form + sezon verisi)
        home_corners = (
            home_data['form'].get('home_corners_avg', 5.0) * 0.6 +
            home_data['season_current'].get('season_home_corners_avg', 5.0) * 0.4
        )
        away_corners = (
            away_data['form'].get('away_corners_avg', 4.5) * 0.6 +
            away_data['season_current'].get('season_away_corners_avg', 4.5) * 0.4
        )
        
        total_corners = home_corners + away_corners
        
        corner_predictions = {
            'total': {
                'over_8.5': int(min(90, max(20, (total_corners - 8.5) * 12))),
                'over_10.5': int(min(85, max(15, (total_corners - 10.5) * 10))),
                'over_12.5': int(min(80, max(10, (total_corners - 12.5) * 8))),
                'over_14.5': int(min(75, max(5, (total_corners - 14.5) * 6)))
            },
            'home_team': {
                'over_4.5': int(min(85, max(20, (home_corners - 4.5) * 15))),
                'over_5.5': int(min(80, max(15, (home_corners - 5.5) * 12))),
                'over_6.5': int(min(75, max(10, (home_corners - 6.5) * 10))),
                'over_7.5': int(min(70, max(5, (home_corners - 7.5) * 8)))
            },
            'away_team': {
                'over_2.5': int(min(80, max(25, (away_corners - 2.5) * 18))),
                'over_3.5': int(min(75, max(20, (away_corners - 3.5) * 15))),
                'over_4.5': int(min(70, max(15, (away_corners - 4.5) * 12))),
                'over_5.5': int(min(65, max(10, (away_corners - 5.5) * 10)))
            }
        }
        
        # Kart tahmini
        home_cards = (
            home_data['form'].get('home_cards_avg', 2.0) * 0.6 +
            home_data['season_current'].get('season_home_cards_avg', 2.0) * 0.4
        )
        away_cards = (
            away_data['form'].get('away_cards_avg', 2.2) * 0.6 +
            away_data['season_current'].get('season_away_cards_avg', 2.2) * 0.4
        )
        
        total_cards = home_cards + away_cards
        
        card_predictions = {
            'total': {
                'over_3.5': int(min(85, max(20, (total_cards - 3.5) * 20))),
                'over_4.5': int(min(80, max(15, (total_cards - 4.5) * 18))),
                'over_5.5': int(min(75, max(10, (total_cards - 5.5) * 15))),
                'over_6.5': int(min(70, max(5, (total_cards - 6.5) * 12)))
            },
            'home_team': {
                'over_1.5': int(min(85, max(30, (home_cards - 1.5) * 35))),
                'over_2.5': int(min(75, max(20, (home_cards - 2.5) * 25))),
                'over_3.5': int(min(65, max(15, (home_cards - 3.5) * 20)))
            },
            'away_team': {
                'over_1.5': int(min(80, max(25, (away_cards - 1.5) * 30))),
                'over_2.5': int(min(70, max(20, (away_cards - 2.5) * 22))),
                'over_3.5': int(min(60, max(15, (away_cards - 3.5) * 18)))
            }
        }
        
        return {
            'corners': corner_predictions,
            'cards': card_predictions
        }

# Test
if __name__ == "__main__":
    predictor = AdvancedPredictor()
    
    print("Gelişmiş tahmin testi...")
    result = predictor.predict_match_outcome("Arsenal", "Manchester City")
    print(f"Sonuç: {result}")
    
    goals = predictor.predict_goal_markets("Arsenal", "Manchester City")
    print(f"Gol pazarları: {goals}")