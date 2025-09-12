import random
from data_collector import DataCollector

class AdvancedPredictor:
    def __init__(self):
        self.collector = DataCollector()
    
    def get_enhanced_team_stats(self, team_name):  # def önüne 4 boşluk ekle
        """Daha detaylı istatistikler"""
        enhanced_stats = {
            'Manchester City': {
                'form': 0.85, 'goals_avg': 2.3, 'conceded_avg': 0.8,
                'corners_avg': 6.8, 'cards_avg': 1.9, 'home_goals': 2.8, 'away_goals': 1.9
            },
            'Arsenal': {
                'form': 0.72, 'goals_avg': 1.8, 'conceded_avg': 1.1,
                'corners_avg': 5.2, 'cards_avg': 2.2, 'home_goals': 2.1, 'away_goals': 1.5
            },
            'Liverpool': {
                'form': 0.78, 'goals_avg': 2.1, 'conceded_avg': 0.9,
                'corners_avg': 6.1, 'cards_avg': 2.0, 'home_goals': 2.4, 'away_goals': 1.8
            },
            'Chelsea': {
                'form': 0.65, 'goals_avg': 1.6, 'conceded_avg': 1.3,
                'corners_avg': 4.9, 'cards_avg': 2.4, 'home_goals': 1.8, 'away_goals': 1.4
            }
        }
        
        return enhanced_stats.get(team_name, {
            'form': 0.6, 'goals_avg': 1.5, 'conceded_avg': 1.2,
            'corners_avg': 5.0, 'cards_avg': 2.2, 'home_goals': 1.7, 'away_goals': 1.3
        })
        
    def predict_1x2(self, home_team, away_team):
        """1X2 + İlk Yarı sonucu"""
        home_stats = self.get_enhanced_team_stats(home_team)
        away_stats = self.get_enhanced_team_stats(away_team)
        
        home_strength = home_stats['form'] + 0.15  # Ev avantajı
        away_strength = away_stats['form']
        
        total = home_strength + away_strength + 0.25
        
        # Full Time
        ft_home = int((home_strength / total) * 100)
        ft_draw = int((0.25 / total) * 100)
        ft_away = 100 - ft_home - ft_draw
        
        # Half Time (daha konservatif)
        ht_home = int(ft_home * 0.7)
        ht_draw = int(ft_draw * 1.4)
        ht_away = 100 - ht_home - ht_draw
        
        return {
            'full_time': (ft_home, ft_draw, ft_away),
            'half_time': (ht_home, ht_draw, ht_away)
        }
    
    def predict_team_totals(self, home_team, away_team):
        """Takım bazlı over/under tahminleri"""
        home_stats = self.get_enhanced_team_stats(home_team)
        away_stats = self.get_enhanced_team_stats(away_team)
        
        home_expected = home_stats['home_goals']
        away_expected = away_stats['away_goals']
        
        predictions = {}
        
        # Home team totals
        predictions['home_team'] = {
            'over_0.5': int(min(95, home_expected * 45)),
            'over_1.5': int(min(85, home_expected * 35)),
            'over_2.5': int(min(75, home_expected * 25))
        }
        
        # Away team totals  
        predictions['away_team'] = {
            'over_0.5': int(min(90, away_expected * 40)),
            'over_1.5': int(min(80, away_expected * 30)),
            'over_2.5': int(min(70, away_expected * 20))
        }
        
        # Total goals
        total_expected = home_expected + away_expected
        predictions['total'] = {
            'over_1.5': int(min(95, total_expected * 35)),
            'over_2.5': int(min(85, total_expected * 25)),
            'over_3.5': int(min(75, total_expected * 18))
        }
        
        return predictions

    def predict_corners_cards(self, home_team, away_team):  # Bu satırı düzelt
        """Detaylı korner ve kart tahminleri"""
        home_stats = self.get_enhanced_team_stats(home_team)
        away_stats = self.get_enhanced_team_stats(away_team)
        
        # CORNER TAHMİNLERİ
        home_corners = home_stats['corners_avg'] * 0.6  # Ev sahibi daha fazla korner alır
        away_corners = away_stats['corners_avg'] * 0.4
        total_corners = home_corners + away_corners
        
        corner_predictions = {
            # Total corners
            'total': {
                'over_8.5': int(min(90, total_corners * 8)),
                'over_10.5': int(min(85, total_corners * 6)),
                'over_12.5': int(min(75, total_corners * 4.5)),
                'over_14.5': int(min(65, total_corners * 3))
            },
            # Home team corners
            'home_team': {
                'over_4.5': int(min(85, home_corners * 12)),
                'over_5.5': int(min(75, home_corners * 9)),
                'over_6.5': int(min(65, home_corners * 7)),
                'over_7.5': int(min(55, home_corners * 5))
            },
            # Away team corners  
            'away_team': {
                'over_2.5': int(min(80, away_corners * 15)),
                'over_3.5': int(min(70, away_corners * 12)),
                'over_4.5': int(min(60, away_corners * 9)),
                'over_5.5': int(min(50, away_corners * 6))
            }
        }
        
        # KART TAHMİNLERİ
        home_cards = home_stats['cards_avg']
        away_cards = away_stats['cards_avg']
        total_cards = home_cards + away_cards
        
        card_predictions = {
            # Total cards
            'total': {
                'over_3.5': int(min(85, total_cards * 18)),
                'over_4.5': int(min(75, total_cards * 14)),
                'over_5.5': int(min(65, total_cards * 11)),
                'over_6.5': int(min(55, total_cards * 8))
            },
            # Home team cards
            'home_team': {
                'over_1.5': int(min(85, home_cards * 35)),
                'over_2.5': int(min(70, home_cards * 25)),
                'over_3.5': int(min(55, home_cards * 18))
            },
            # Away team cards
            'away_team': {
                'over_1.5': int(min(80, away_cards * 32)),
                'over_2.5': int(min(65, away_cards * 22)),
                'over_3.5': int(min(50, away_cards * 15))
            }
        }
        
        return {
            'corners': corner_predictions,
            'cards': card_predictions
        }
        
    def predict_btts(self, home_team, away_team):
        """BTTS tahmini"""
        home_stats = self.get_enhanced_team_stats(home_team)
        away_stats = self.get_enhanced_team_stats(away_team)
        
        btts_prob = int((home_stats['home_goals'] + away_stats['away_goals']) * 25)
        btts_prob = min(85, max(25, btts_prob))
        
        return btts_prob, 100 - btts_prob

# Test
if __name__ == "__main__":
    predictor = AdvancedPredictor()
    
    match_pred = predictor.predict_1x2("Manchester City", "Arsenal")
    totals = predictor.predict_team_totals("Manchester City", "Arsenal")
    corners_cards = predictor.predict_corners_cards("Manchester City", "Arsenal")
    
    print("1X2 Full Time:", match_pred['full_time'])
    print("Home O1.5:", totals['home_team']['over_1.5'])
    print("Corners O10.5:", corners_cards['corners']['total']['over_10.5'])