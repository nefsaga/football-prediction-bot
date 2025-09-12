import math
from real_data_collector import RealDataCollector

class EnhancedPredictor:
    def __init__(self):
        self.collector = RealDataCollector()
        self.historical_data = self.collector.get_historical_data()
        
    def get_team_stats(self, team_name):
        """Gerçek takım verilerini al"""
        # Takım ismi eşleştirmesi
        team_mapping = self.collector.get_team_mappings()
        mapped_name = team_mapping.get(team_name, team_name)
        
        # Geçmiş verilerde ara
        if mapped_name in self.historical_data:
            return self.historical_data[mapped_name]
        
        # Bulunamazsa ortalama değerler
        return {
            'home_goals_avg': 1.5, 'away_goals_avg': 1.2,
            'home_conceded_avg': 1.2, 'away_conceded_avg': 1.5,
            'home_corners_avg': 5.0, 'away_corners_avg': 4.5,
            'home_cards_avg': 2.0, 'away_cards_avg': 2.2,
            'total_games': 38
        }
    
    def calculate_poisson_probability(self, expected_goals, actual_goals):
        """Poisson dağılımı ile gol olasılığı"""
        return (math.exp(-expected_goals) * (expected_goals ** actual_goals)) / math.factorial(actual_goals)
    
    def predict_1x2_advanced(self, home_team, away_team):
        """Gelişmiş 1X2 tahmini - Gerçek verilerle"""
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Expected Goals hesaplama
        home_attack = home_stats['home_goals_avg']
        home_defense = home_stats['home_conceded_avg']
        away_attack = away_stats['away_goals_avg'] 
        away_defense = away_stats['away_conceded_avg']
        
        # Lig ortalaması (yaklaşık)
        league_avg_home = 1.6
        league_avg_away = 1.2
        
        # Gerçek expected goals
        home_expected = (home_attack / league_avg_home) * (away_defense / league_avg_away) * league_avg_home
        away_expected = (away_attack / league_avg_away) * (home_defense / league_avg_home) * league_avg_away
        
        # Poisson ile skorlar
        probabilities = {}
        total_prob = 0
        
        for home_goals in range(0, 6):
            for away_goals in range(0, 6):
                home_prob = self.calculate_poisson_probability(home_expected, home_goals)
                away_prob = self.calculate_poisson_probability(away_expected, away_goals)
                match_prob = home_prob * away_prob
                
                probabilities[(home_goals, away_goals)] = match_prob
                total_prob += match_prob
        
        # Sonuç olasılıkları
        home_win_prob = sum([prob for (h, a), prob in probabilities.items() if h > a])
        draw_prob = sum([prob for (h, a), prob in probabilities.items() if h == a])
        away_win_prob = sum([prob for (h, a), prob in probabilities.items() if h < a])
        
        # Normalize et
        total = home_win_prob + draw_prob + away_win_prob
        home_win_prob = int((home_win_prob / total) * 100)
        draw_prob = int((draw_prob / total) * 100)
        away_win_prob = 100 - home_win_prob - draw_prob
        
        # İlk yarı (daha konservatif)
        ht_home = int(home_win_prob * 0.6)
        ht_draw = int(draw_prob * 1.5)
        ht_away = 100 - ht_home - ht_draw
        
        return {
            'full_time': (home_win_prob, draw_prob, away_win_prob),
            'half_time': (ht_home, ht_draw, ht_away),
            'expected_goals': (round(home_expected, 2), round(away_expected, 2))
        }
    
    def predict_totals_advanced(self, home_team, away_team):
        """Gerçek verilerle gol tahminleri"""
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Expected goals (daha doğru hesaplama)
        home_expected = (home_stats['home_goals_avg'] + away_stats['away_conceded_avg']) / 2
        away_expected = (away_stats['away_goals_avg'] + home_stats['home_conceded_avg']) / 2
        
        total_expected = home_expected + away_expected
        
        predictions = {}
        
        # Home team predictions
        predictions['home_team'] = {
            'over_0.5': int(min(95, (1 - self.calculate_poisson_probability(home_expected, 0)) * 100)),
            'over_1.5': int(min(90, (1 - self.calculate_poisson_probability(home_expected, 0) - self.calculate_poisson_probability(home_expected, 1)) * 100)),
            'over_2.5': int(min(85, (1 - sum([self.calculate_poisson_probability(home_expected, i) for i in range(3)])) * 100))
        }
        
        # Away team predictions  
        predictions['away_team'] = {
            'over_0.5': int(min(90, (1 - self.calculate_poisson_probability(away_expected, 0)) * 100)),
            'over_1.5': int(min(85, (1 - self.calculate_poisson_probability(away_expected, 0) - self.calculate_poisson_probability(away_expected, 1)) * 100)),
            'over_2.5': int(min(80, (1 - sum([self.calculate_poisson_probability(away_expected, i) for i in range(3)])) * 100))
        }
        
        # Total goals
        predictions['total'] = {
            'over_1.5': int(min(95, 100 - (self.calculate_poisson_probability(total_expected, 0) + self.calculate_poisson_probability(total_expected, 1)) * 100)),
            'over_2.5': int(min(90, 100 - sum([self.calculate_poisson_probability(total_expected, i) for i in range(3)]) * 100)),
            'over_3.5': int(min(85, 100 - sum([self.calculate_poisson_probability(total_expected, i) for i in range(4)]) * 100))
        }
        
        return predictions
    
    def predict_corners_cards_advanced(self, home_team, away_team):
        """Gerçek verilerle korner/kart tahminleri"""
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Korner tahminleri (gerçek averajlar)
        home_corners_expected = home_stats['home_corners_avg']
        away_corners_expected = away_stats['away_corners_avg']
        total_corners = home_corners_expected + away_corners_expected
        
        corner_predictions = {
            'total': {
                'over_8.5': int(min(90, max(20, (total_corners - 8.5) * 15))),
                'over_10.5': int(min(85, max(15, (total_corners - 10.5) * 12))),
                'over_12.5': int(min(80, max(10, (total_corners - 12.5) * 10))),
                'over_14.5': int(min(75, max(5, (total_corners - 14.5) * 8)))
            },
            'home_team': {
                'over_4.5': int(min(85, max(20, (home_corners_expected - 4.5) * 18))),
                'over_5.5': int(min(80, max(15, (home_corners_expected - 5.5) * 15))),
                'over_6.5': int(min(75, max(10, (home_corners_expected - 6.5) * 12))),
                'over_7.5': int(min(70, max(5, (home_corners_expected - 7.5) * 10)))
            },
            'away_team': {
                'over_2.5': int(min(80, max(25, (away_corners_expected - 2.5) * 20))),
                'over_3.5': int(min(75, max(20, (away_corners_expected - 3.5) * 18))),
                'over_4.5': int(min(70, max(15, (away_corners_expected - 4.5) * 15))),
                'over_5.5': int(min(65, max(10, (away_corners_expected - 5.5) * 12)))
            }
        }
        
        # Kart tahminleri (gerçek averajlar)
        home_cards_expected = home_stats['home_cards_avg']
        away_cards_expected = away_stats['away_cards_avg']
        total_cards = home_cards_expected + away_cards_expected
        
        card_predictions = {
            'total': {
                'over_3.5': int(min(85, max(20, (total_cards - 3.5) * 25))),
                'over_4.5': int(min(80, max(15, (total_cards - 4.5) * 20))),
                'over_5.5': int(min(75, max(10, (total_cards - 5.5) * 18))),
                'over_6.5': int(min(70, max(5, (total_cards - 6.5) * 15)))
            },
            'home_team': {
                'over_1.5': int(min(85, max(30, (home_cards_expected - 1.5) * 40))),
                'over_2.5': int(min(75, max(20, (home_cards_expected - 2.5) * 30))),
                'over_3.5': int(min(65, max(15, (home_cards_expected - 3.5) * 25)))
            },
            'away_team': {
                'over_1.5': int(min(80, max(25, (away_cards_expected - 1.5) * 35))),
                'over_2.5': int(min(70, max(20, (away_cards_expected - 2.5) * 28))),
                'over_3.5': int(min(60, max(15, (away_cards_expected - 3.5) * 22)))
            }
        }
        
        return {
            'corners': corner_predictions,
            'cards': card_predictions
        }
    
    def predict_btts_advanced(self, home_team, away_team):
        """Gelişmiş BTTS tahmini"""
        home_stats = self.get_team_stats(home_team)
        away_stats = self.get_team_stats(away_team)
        
        # Her iki takımın gol atma olasılığı
        home_scores_prob = 1 - self.calculate_poisson_probability(home_stats['home_goals_avg'], 0)
        away_scores_prob = 1 - self.calculate_poisson_probability(away_stats['away_goals_avg'], 0)
        
        # BTTS olasılığı
        btts_prob = int(home_scores_prob * away_scores_prob * 100)
        btts_prob = min(85, max(25, btts_prob))
        
        return btts_prob, 100 - btts_prob

# Test
if __name__ == "__main__":
    predictor = EnhancedPredictor()
    
    result = predictor.predict_1x2_advanced("Arsenal", "Manchester City")
    print("Advanced 1X2:", result)
    
    totals = predictor.predict_totals_advanced("Arsenal", "Manchester City")
    print("Total O2.5:", totals['total']['over_2.5'])