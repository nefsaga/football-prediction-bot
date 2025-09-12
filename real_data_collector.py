import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class RealDataCollector:
    def __init__(self, league_code='E0'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.league_code = league_code
        self.league_config = self.get_league_config()
        
        # Sezon kodları
        self.current_season = "2526"
        self.previous_season = "2425"
        self.older_season = "2324"
    
    def get_league_config(self):
        """Lig konfigürasyonları"""
        configs = {
            'E0': {
                'name': 'Premier League',
                'country': 'England',
                'teams': {
                    'Arsenal': 'Arsenal',
                    'Man City': 'Manchester City',
                    'Man United': 'Manchester United',
                    'Liverpool': 'Liverpool',
                    'Chelsea': 'Chelsea',
                    'Tottenham': 'Tottenham',
                    'Newcastle': 'Newcastle',
                    'Brighton': 'Brighton',
                    'Aston Villa': 'Aston Villa',
                    'West Ham': 'West Ham',
                    'Crystal Palace': 'Crystal Palace',
                    'Fulham': 'Fulham',
                    'Wolves': 'Wolves',
                    'Everton': 'Everton',
                    'Brentford': 'Brentford',
                    "Nott'm Forest": 'Nottingham Forest',
                    'Leicester': 'Leicester City',
                    'Ipswich': 'Ipswich Town',
                    'Southampton': 'Southampton',
                    'Bournemouth': 'Bournemouth'
                }
            },
            'T1': {
                'name': 'Süper Lig',
                'country': 'Turkey',
                'teams': {
                    'Ad. Demirspor': 'Adana Demirspor',
                    'Alanyaspor': 'Alanyaspor',
                    'Antalyaspor': 'Antalyaspor',
                    'Besiktas': 'Beşiktaş',
                    'Bodrumspor': 'Bodrumspor',
                    'Buyuksehyr': 'Başakşehir',
                    'Eyupspor': 'Eyüpspor',
                    'Fenerbahce': 'Fenerbahçe',
                    'Galatasaray': 'Galatasaray',
                    'Gaziantep': 'Gaziantep FK',
                    'Goztep': 'Göztepe',
                    'Hatayspor': 'Hatayspor',
                    'Kasimpasa': 'Kasımpaşa',
                    'Kayserispor': 'Kayserispor',
                    'Konyaspor': 'Konyaspor',
                    'Rizespor': 'Çaykur Rizespor',
                    'Samsunspor': 'Samsunspor',
                    'Sivasspor': 'Sivasspor',
                    'Trabzonspor': 'Trabzonspor'
                }
            },
            'D1': {
                'name': 'Bundesliga',
                'country': 'Germany',
                'teams': {
                    'Augsburg': 'Augsburg',
                    'Bayern Munich': 'Bayern Munich',
                    'Bochum': 'Bochum',
                    'Dortmund': 'Dortmund',
                    'Ein Frankfurt': 'Ein Frankfurt',
                    'Freiburg': 'Freiburg',
                    'Heidenheim': 'Heidenheim',
                    'Hoffenheim': 'Hoffenheim',
                    'Holstein Kiel': 'Holstein Kiel',
                    'Leverkusen': 'Leverkusen',
                    'M\'gladbach': 'M\'gladbach',
                    'Mainz': 'Mainz',
                    'RB Leipzig': 'RB Leipzig',
                    'St Pauli': 'St Pauli',
                    'Stuttgart': 'Stuttgart',
                    'Union Berlin': 'Union Berlin',
                    'Werder Bremen': 'Werder Bremen',
                    'Wolfsburg': 'Wolfsburg'
                }
            },
            'D2': {
                'name': '2.Bundesliga',
                'country': 'Germany',
                'teams': {
                    'Braunschweig': 'Braunschweig',
                    'Darmstadt': 'Darmstadt',
                    'Elversberg': 'Elversberg',
                    'FC Koln': 'FC Koln',
                    'Fortuna Dusseldorf': 'Fortuna Dusseldorf',
                    'Greuther Furth': 'Greuther Furth',
                    'Hamburg': 'Hamburg',
                    'Hannover': 'Hannover',
                    'Hertha': 'Hertha',
                    'Kaiserslautern': 'Kaiserslautern',
                    'Karlsruhe': 'Karlsruhe',
                    'Magdeburg': 'Magdeburg',
                    'Nurnberg': 'Nurnberg',
                    'Paderborn': 'Paderborn',
                    'Preußen Münster': 'Preußen Münster',
                    'Regensburg': 'Regensburg',
                    'Schalke 04': 'Schalke 04',
                    'Ulm': 'Ulm'
                }
            },
            'F1': {
                'name': 'Ligue 1',
                'country': 'France',
                'teams': {
                    'Angers': 'Angers',
                    'Auxerre': 'Auxerre',
                    'Brest': 'Brest',
                    'Le Havre': 'Le Havre',
                    'Lens': 'Lens',
                    'Lille': 'Lille',
                    'Lyon': 'Lyon',
                    'Marseille': 'Marseille',
                    'Monaco': 'Monaco',
                    'Montpellier': 'Montpellier',
                    'Nantes': 'Nantes',
                    'Nice': 'Nice',
                    'Paris SG': 'Paris SG',
                    'Reims': 'Reims',
                    'Rennes': 'Rennes',
                    'St Etienne': 'St Etienne',
                    'Strasbourg': 'Strasbourg',
                    'Toulouse': 'Toulouse'
                }
            },
            'B1': {
                'name': 'Jupiler Pro League',
                'country': 'Belgium',
                'teams': {
                    'Anderlecht': 'Anderlecht',
                    'Antwerp': 'Antwerp',
                    'Beerschot VA': 'Beerschot VA',
                    'Cercle Brugge': 'Cercle Brugge',
                    'Charleroi': 'Charleroi',
                    'Club Brugge': 'Club Brugge',
                    'Dender': 'Dender',
                    'Genk': 'Genk',
                    'Gent': 'Gent',
                    'Kortrijk': 'Kortrijk',
                    'Mechelen': 'Mechelen',
                    'Oud-Heverlee Leuven': 'Oud-Heverlee Leuven',
                    'St Truiden': 'St Truiden',
                    'St. Gilloise': 'St. Gilloise',
                    'Standard': 'Standard',
                    'Westerlo': 'Westerlo'
                }
            },
            'SP1': {
                'name': 'La Liga',
                'country': 'Spain',
                'teams': {
                    'Alaves': 'Alaves',
                    'Ath Bilbao': 'Ath Bilbao',
                    'Ath Madrid': 'Ath Madrid',
                    'Barcelona': 'Barcelona',
                    'Betis': 'Betis',
                    'Celta': 'Celta',
                    'Espanol': 'Espanol',
                    'Getafe': 'Getafe',
                    'Girona': 'Girona',
                    'Las Palmas': 'Las Palmas',
                    'Leganes': 'Leganes',
                    'Mallorca': 'Mallorca',
                    'Osasuna': 'Osasuna',
                    'Real Madrid': 'Real Madrid',
                    'Sevilla': 'Sevilla',
                    'Sociedad': 'Sociedad',
                    'Valencia': 'Valencia',
                    'Valladolid': 'Valladolid',
                    'Vallecano': 'Vallecano',
                    'Villarreal': 'Villarreal'
                }
            },
            'SP2': {
                'name': 'La Liga 2',
                'country': 'Spain',
                'teams': {
                    'Albacete': 'Albacete',
                    'Almeria': 'Almeria',
                    'Burgos': 'Burgos',
                    'Cadiz': 'Cadiz',
                    'Cartagena': 'Cartagena',
                    'Castellon': 'Castellon',
                    'Cordoba': 'Cordoba',
                    'Eibar': 'Eibar',
                    'Elche': 'Elche',
                    'Eldense': 'Eldense',
                    'Ferrol': 'Ferrol',
                    'Granada': 'Granada',
                    'Huesca': 'Huesca',
                    'La Coruna': 'La Coruna',
                    'Levante': 'Levante',
                    'Malaga': 'Malaga',
                    'Mirandes': 'Mirandes',
                    'Oviedo': 'Oviedo',
                    'Santander': 'Santander',
                    'Sp Gijon': 'Sp Gijon',
                    'Tenerife': 'Tenerife',
                    'Zaragoza': 'Zaragoza'
                }
            },
            'I1': {
                'name': 'Serie A',
                'country': 'Italy',
                'teams': {
                    'Atalanta': 'Atalanta',
                    'Bologna': 'Bologna',
                    'Cagliari': 'Cagliari',
                    'Como': 'Como',
                    'Empoli': 'Empoli',
                    'Fiorentina': 'Fiorentina',
                    'Genoa': 'Genoa',
                    'Inter': 'Inter',
                    'Juventus': 'Juventus',
                    'Lazio': 'Lazio',
                    'Lecce': 'Lecce',
                    'Milan': 'Milan',
                    'Monza': 'Monza',
                    'Napoli': 'Napoli',
                    'Parma': 'Parma',
                    'Roma': 'Roma',
                    'Torino': 'Torino',
                    'Udinese': 'Udinese',
                    'Venezia': 'Venezia',
                    'Verona': 'Verona'
                }
            },
            'I2': {
                'name': 'Serie B',
                'country': 'Italy',
                'teams': {
                    'Bari': 'Bari',
                    'Brescia': 'Brescia',
                    'Carrarese': 'Carrarese',
                    'Catanzaro': 'Catanzaro',
                    'Cesena': 'Cesena',
                    'Cittadella': 'Cittadella',
                    'Cosenza': 'Cosenza',
                    'Cremonese': 'Cremonese',
                    'Frosinone': 'Frosinone',
                    'Juve Stabia': 'Juve Stabia',
                    'Mantova': 'Mantova',
                    'Modena': 'Modena',
                    'Palermo': 'Palermo',
                    'Pisa': 'Pisa',
                    'Reggiana': 'Reggiana',
                    'Salernitana': 'Salernitana',
                    'Sampdoria': 'Sampdoria',
                    'Sassuolo': 'Sassuolo',
                    'Spezia': 'Spezia',
                    'Sudtirol': 'Sudtirol'
                }
            },
            'P1': {
                'name': 'Primeira Liga',
                'country': 'Portugal',
                'teams': {
                    'AVS': 'AVS',
                    'Arouca': 'Arouca',
                    'Benfica': 'Benfica',
                    'Boavista': 'Boavista',
                    'Casa Pia': 'Casa Pia',
                    'Estoril': 'Estoril',
                    'Estrela': 'Estrela',
                    'Famalicao': 'Famalicao',
                    'Farense': 'Farense',
                    'Gil Vicente': 'Gil Vicente',
                    'Guimaraes': 'Guimaraes',
                    'Moreirense': 'Moreirense',
                    'Nacional': 'Nacional',
                    'Porto': 'Porto',
                    'Rio Ave': 'Rio Ave',
                    'Santa Clara': 'Santa Clara',
                    'Sp Braga': 'Sp Braga',
                    'Sp Lisbon': 'Sp Lisbon'
                }
            }
        }
        
        return configs.get(self.league_code, configs['E0'])
    
    def get_team_mappings(self):
        """Mevcut lig için takım mapping'i döndür"""
        return self.league_config['teams']
    
    def fetch_current_season_data(self):
        """2025-26 sezon verisi"""
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{self.current_season}/{self.league_code}.csv"
            current_df = pd.read_csv(url)
            print(f"✅ {self.league_config['name']} 2025-26: {len(current_df)} maç verisi alındı")
            return current_df
        except Exception as e:
            print(f"⚠️ Mevcut sezon verisi alınamadı: {e}")
            return pd.DataFrame()
    
    def fetch_previous_season_data(self):
        """2024-25 sezon verisi"""
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{self.previous_season}/{self.league_code}.csv"
            previous_df = pd.read_csv(url)
            print(f"✅ {self.league_config['name']} 2024-25: {len(previous_df)} maç verisi alındı")
            return previous_df
        except Exception as e:
            print(f"❌ Önceki sezon verisi alınamadı: {e}")
            return pd.DataFrame()
    
    def fetch_older_season_data(self):
        """2023-24 sezon verisi"""
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{self.older_season}/{self.league_code}.csv"
            older_df = pd.read_csv(url)
            print(f"✅ {self.league_config['name']} 2023-24: {len(older_df)} maç verisi alındı")
            return older_df
        except Exception as e:
            print(f"❌ 2023-24 sezon verisi alınamadı: {e}")
            return pd.DataFrame()
    
    def fetch_extended_historical_data(self):
        """H2H için 4 sezon verisi"""
        seasons = ["2223", "2324", "2425", "2526"]
        all_data = []
        
        for season in seasons:
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{season}/{self.league_code}.csv"
                df = pd.read_csv(url)
                df['Season'] = season
                all_data.append(df)
                print(f"✅ {self.league_config['name']} {season}: {len(df)} maç H2H için alındı")
            except Exception as e:
                print(f"⚠️ {season} sezonu alınamadı: {e}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"✅ {self.league_config['name']} toplam H2H verisi: {len(combined_df)} maç")
            return combined_df
        
        return pd.DataFrame()
    
    def get_head_to_head_matches(self, team1, team2, df, n=5, venue=None):
        """İki takım arasındaki son N maçı al"""
        if df.empty:
            return pd.DataFrame()
            
        # Tarih sütununu datetime'a çevir
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values('Date')
        
        if venue == 'team1_home':
            # team1 ev sahibi, team2 deplasman
            h2h_matches = df[(df['HomeTeam'] == team1) & (df['AwayTeam'] == team2)]
        elif venue == 'team2_home':
            # team2 ev sahibi, team1 deplasman  
            h2h_matches = df[(df['HomeTeam'] == team2) & (df['AwayTeam'] == team1)]
        else:
            # Tüm karşılaşmalar
            h2h_matches = df[
                ((df['HomeTeam'] == team1) & (df['AwayTeam'] == team2)) |
                ((df['HomeTeam'] == team2) & (df['AwayTeam'] == team1))
            ]
        
        return h2h_matches.tail(n)
    
    def analyze_h2h_performance(self, team1, team2, games_df, analysis_type):
        """Head-to-head performans analizi"""
        if len(games_df) == 0:
            return {
                f'{analysis_type}_h2h_games': 0,
                f'{analysis_type}_h2h_wins': 0,
                f'{analysis_type}_h2h_draws': 0,
                f'{analysis_type}_h2h_losses': 0,
                f'{analysis_type}_h2h_goals_avg': 0,
                f'{analysis_type}_h2h_conceded_avg': 0,
                f'{analysis_type}_h2h_win_rate': 0,
                f'{analysis_type}_h2h_form_points': 0
            }
        
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        
        for _, game in games_df.iterrows():
            if game['HomeTeam'] == team1:
                # team1 ev sahibi
                team1_goals = game['FTHG']
                team2_goals = game['FTAG']
            else:
                # team1 deplasman
                team1_goals = game['FTAG']
                team2_goals = game['FTHG']
            
            goals_scored += team1_goals
            goals_conceded += team2_goals
            
            if team1_goals > team2_goals:
                wins += 1
            elif team1_goals == team2_goals:
                draws += 1
            else:
                losses += 1
        
        games_count = len(games_df)
        points = (wins * 3) + draws
        
        return {
            f'{analysis_type}_h2h_games': games_count,
            f'{analysis_type}_h2h_wins': wins,
            f'{analysis_type}_h2h_draws': draws,
            f'{analysis_type}_h2h_losses': losses,
            f'{analysis_type}_h2h_goals_avg': round(goals_scored / games_count, 2),
            f'{analysis_type}_h2h_conceded_avg': round(goals_conceded / games_count, 2),
            f'{analysis_type}_h2h_win_rate': round((wins / games_count) * 100, 1),
            f'{analysis_type}_h2h_form_points': points,
            f'{analysis_type}_h2h_point_avg': round(points / games_count, 2)
        }
    
    def get_comprehensive_h2h_analysis(self, team1, team2, historical_df):
        """Kapsamlı H2H analizi"""
        h2h_stats = {}
        
        # 1. Genel H2H (son 5 maç)
        all_h2h = self.get_head_to_head_matches(team1, team2, historical_df, n=5)
        general_h2h = self.analyze_h2h_performance(team1, team2, all_h2h, 'general')
        h2h_stats.update(general_h2h)
        
        # 2. team1 ev sahibi olduğunda (son 5 maç)
        team1_home_h2h = self.get_head_to_head_matches(team1, team2, historical_df, n=5, venue='team1_home')
        home_h2h = self.analyze_h2h_performance(team1, team2, team1_home_h2h, 'home')
        h2h_stats.update(home_h2h)
        
        # 3. team1 deplasman olduğunda (son 5 maç)  
        team1_away_h2h = self.get_head_to_head_matches(team1, team2, historical_df, n=5, venue='team2_home')
        away_h2h = self.analyze_h2h_performance(team1, team2, team1_away_h2h, 'away')
        h2h_stats.update(away_h2h)
        
        return h2h_stats
    
    def get_last_n_games_by_venue(self, team, df, n=5, venue='all'):
        """Takımın son N maçını saha durumuna göre al"""
        if df.empty:
            return pd.DataFrame()
            
        # Tarih sütununu datetime'a çevir
        df = df.copy()
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values('Date')
        
        if venue == 'home':
            # Sadece ev sahibi maçları
            team_games = df[df['HomeTeam'] == team]
        elif venue == 'away':
            # Sadece deplasman maçları
            team_games = df[df['AwayTeam'] == team]
        else:
            # Tüm maçlar
            team_games = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)]
        
        # Son N maç
        return team_games.tail(n)
    
    def analyze_games_performance(self, team, games_df, venue_type):
        """Maç performansını analiz et"""
        if len(games_df) == 0:
            return {
                f'{venue_type}_games_count': 0,
                f'{venue_type}_form_points': 0,
                f'{venue_type}_form_avg': 0,
                f'{venue_type}_goals_avg': 0,
                f'{venue_type}_conceded_avg': 0,
                f'{venue_type}_corners_avg': 0,
                f'{venue_type}_cards_avg': 0,
                f'{venue_type}_wins': 0,
                f'{venue_type}_draws': 0,
                f'{venue_type}_losses': 0,
                f'{venue_type}_win_rate': 0
            }
        
        points = 0
        goals_scored = 0
        goals_conceded = 0
        corners_total = 0
        cards_total = 0
        wins = 0
        draws = 0
        losses = 0
        
        for _, game in games_df.iterrows():
            if game['HomeTeam'] == team:
                # Ev sahibi olarak
                team_goals = game['FTHG']
                opponent_goals = game['FTAG']
                team_corners = game['HC'] if pd.notna(game['HC']) else 0
                team_cards = (game['HY'] if pd.notna(game['HY']) else 0) + (game['HR'] if pd.notna(game['HR']) else 0)
            else:
                # Deplasman olarak
                team_goals = game['FTAG'] 
                opponent_goals = game['FTHG']
                team_corners = game['AC'] if pd.notna(game['AC']) else 0
                team_cards = (game['AY'] if pd.notna(game['AY']) else 0) + (game['AR'] if pd.notna(game['AR']) else 0)
            
            goals_scored += team_goals
            goals_conceded += opponent_goals
            corners_total += team_corners
            cards_total += team_cards
            
            # Sonuç analizi
            if team_goals > opponent_goals:
                points += 3
                wins += 1
            elif team_goals == opponent_goals:
                points += 1
                draws += 1
            else:
                losses += 1
        
        games_count = len(games_df)
        
        return {
            f'{venue_type}_games_count': games_count,
            f'{venue_type}_form_points': points,
            f'{venue_type}_form_avg': round(points / games_count, 2),
            f'{venue_type}_goals_avg': round(goals_scored / games_count, 2),
            f'{venue_type}_conceded_avg': round(goals_conceded / games_count, 2),
            f'{venue_type}_corners_avg': round(corners_total / games_count, 2),
            f'{venue_type}_cards_avg': round(cards_total / games_count, 2),
            f'{venue_type}_wins': wins,
            f'{venue_type}_draws': draws,
            f'{venue_type}_losses': losses,
            f'{venue_type}_win_rate': round((wins / games_count) * 100, 1)
        }
    
    def calculate_comprehensive_form(self, team, current_df, previous_df, older_df=None):
        """Kapsamlı form analizi - 3 sezon verisi"""
        # Üç sezonu birleştir (en yeniden en eskiye)
        if older_df is not None and not older_df.empty:
            combined_df = pd.concat([older_df, previous_df, current_df], ignore_index=True)
        else:
            combined_df = pd.concat([previous_df, current_df], ignore_index=True)
        
        # Son 10 maç (genel)
        last_10_all = self.get_last_n_games_by_venue(team, combined_df, n=10, venue='all')
        overall_form = self.analyze_games_performance(team, last_10_all, 'overall')
        
        # Son 5 ev sahibi maçı
        last_5_home = self.get_last_n_games_by_venue(team, combined_df, n=5, venue='home')
        home_form = self.analyze_games_performance(team, last_5_home, 'home')
        
        # Son 5 deplasman maçı
        last_5_away = self.get_last_n_games_by_venue(team, combined_df, n=5, venue='away')
        away_form = self.analyze_games_performance(team, last_5_away, 'away')
        
        # Tüm istatistikleri birleştir
        form_stats = {}
        form_stats.update(overall_form)
        form_stats.update(home_form)
        form_stats.update(away_form)
        
        return form_stats
    
    def calculate_season_stats(self, team, df):
        """Sezon bazlı istatistikler"""
        if df.empty:
            return {}
        
        home_games = df[df['HomeTeam'] == team]
        away_games = df[df['AwayTeam'] == team]
        
        stats = {}
        
        if len(home_games) > 0:
            stats['season_home_goals_avg'] = round(home_games['FTHG'].mean(), 2)
            stats['season_home_conceded_avg'] = round(home_games['FTAG'].mean(), 2)
            stats['season_home_corners_avg'] = round(home_games['HC'].mean(), 2)
            stats['season_home_cards_avg'] = round((home_games['HY'] + home_games['HR']).mean(), 2)
        
        if len(away_games) > 0:
            stats['season_away_goals_avg'] = round(away_games['FTAG'].mean(), 2)
            stats['season_away_conceded_avg'] = round(away_games['FTHG'].mean(), 2)
            stats['season_away_corners_avg'] = round(away_games['AC'].mean(), 2)
            stats['season_away_cards_avg'] = round((away_games['AY'] + away_games['AR']).mean(), 2)
        
        return stats

    def get_match_analysis(self, home_team, away_team):
        """Belirli bir maç için kapsamlı analiz - 3 sezon dahil"""
        # Mapping tersine çevir (bizim isimler -> CSV isimleri)
        reverse_mapping = {v: k for k, v in self.get_team_mappings().items()}
        
        # CSV'deki gerçek isimleri al
        home_team_csv = reverse_mapping.get(home_team, home_team)
        away_team_csv = reverse_mapping.get(away_team, away_team)
        
        print(f"🔍 Analiz ediliyor: {home_team} ({home_team_csv}) vs {away_team} ({away_team_csv})")
        
        # Veri setlerini al
        current_df = self.fetch_current_season_data()      # 2025-26
        previous_df = self.fetch_previous_season_data()    # 2024-25
        older_df = self.fetch_older_season_data()          # 2023-24
        historical_df = self.fetch_extended_historical_data()  # 4 sezon H2H için
        
        analysis = {}
        
        # Her iki takım için form analizi (3 sezon)
        home_form = self.calculate_comprehensive_form(home_team_csv, current_df, previous_df, older_df)
        away_form = self.calculate_comprehensive_form(away_team_csv, current_df, previous_df, older_df)
        
        # Sezon istatistikleri (3 sezon)
        home_season_current = self.calculate_season_stats(home_team_csv, current_df)
        home_season_previous = self.calculate_season_stats(home_team_csv, previous_df)
        home_season_older = self.calculate_season_stats(home_team_csv, older_df)
        
        away_season_current = self.calculate_season_stats(away_team_csv, current_df)
        away_season_previous = self.calculate_season_stats(away_team_csv, previous_df)
        away_season_older = self.calculate_season_stats(away_team_csv, older_df)
        
        # H2H analizi (4 sezon)
        h2h_analysis = self.get_comprehensive_h2h_analysis(home_team_csv, away_team_csv, historical_df)
        
        analysis['home_team'] = {
            'name': home_team,
            'csv_name': home_team_csv,
            'form': home_form,
            'season_current': home_season_current,    # 2025-26
            'season_previous': home_season_previous,  # 2024-25
            'season_older': home_season_older         # 2023-24
        }
        
        analysis['away_team'] = {
            'name': away_team,
            'csv_name': away_team_csv,
            'form': away_form,
            'season_current': away_season_current,
            'season_previous': away_season_previous,
            'season_older': away_season_older
        }
        
        analysis['head_to_head'] = h2h_analysis
        
        return analysis
        
    def fetch_fixtures(self, league_code=None):
        """Lig bazlı fixture sistemi"""
        if league_code:
            self.league_code = league_code
            self.league_config = self.get_league_config()
        
        today = datetime.now()
        
        # Lig bazlı mock fixtures
        fixtures_dict = {
            'T1': [
                {'home_team': 'Galatasaray', 'away_team': 'Fenerbahçe', 'time': '19:00'},
                {'home_team': 'Beşiktaş', 'away_team': 'Trabzonspor', 'time': '21:30'}
            ],
            'SP1': [
                {'home_team': 'Barcelona', 'away_team': 'Real Madrid', 'time': '21:00'},
                {'home_team': 'Ath Madrid', 'away_team': 'Sevilla', 'time': '18:30'}
            ],
            'D1': [
                {'home_team': 'Bayern Munich', 'away_team': 'Dortmund', 'time': '18:30'},
                {'home_team': 'RB Leipzig', 'away_team': 'Leverkusen', 'time': '15:30'}
            ],
            'I1': [
                {'home_team': 'Juventus', 'away_team': 'Inter', 'time': '20:45'},
                {'home_team': 'Milan', 'away_team': 'Roma', 'time': '18:00'}
            ],
            'F1': [
                {'home_team': 'Paris SG', 'away_team': 'Marseille', 'time': '21:00'},
                {'home_team': 'Monaco', 'away_team': 'Lyon', 'time': '17:00'}
            ]
        }
        
        league_fixtures = fixtures_dict.get(self.league_code, [
            {'home_team': 'Arsenal', 'away_team': 'Manchester City', 'time': '17:30'},
            {'home_team': 'Liverpool', 'away_team': 'Chelsea', 'time': '20:00'}
        ])
        
        fixtures = []
        for fixture in league_fixtures:
            fixtures.append({
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'date': today.strftime('%Y-%m-%d'),
                'time': fixture['time'],
                'league': self.league_config['name']
            })
        
        return fixtures

# Test
if __name__ == "__main__":
    print("=== MULTI-LIG TEST ===")
    
    # Test edilen ligler
    test_leagues = ['E0', 'T1', 'SP1', 'D1', 'I1']
    league_names = ['Premier League', 'Süper Lig', 'La Liga', 'Bundesliga', 'Serie A']
    
    for code, name in zip(test_leagues, league_names):
        print(f"\n{name} ({code}) test ediliyor...")
        try:
            collector = RealDataCollector(code)
            fixtures = collector.fetch_fixtures()
            print(f"✅ {name}: {len(fixtures)} maç fixture")
            
            if fixtures:
                fixture = fixtures[0]
                print(f"   Örnek: {fixture['home_team']} vs {fixture['away_team']}")
                
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n🎉 Multi-lig sistemi hazır! 11 lig destekleniyor.")