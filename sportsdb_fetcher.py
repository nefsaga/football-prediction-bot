import requests
from datetime import datetime, timedelta
import json

class SportsDBFetcher:
    def __init__(self):
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3"
        
        # TheSportsDB League ID'leri
        self.league_mappings = {
            'E0': '4328',   # Premier League
            'SP1': '4335',  # La Liga
            'D1': '4331',   # Bundesliga
            'I1': '4332',   # Serie A
            'F1': '4334',   # Ligue 1
            'T1': '4569',   # Süper Lig
            'D2': '4333',   # 2. Bundesliga
            'SP2': '4336',  # La Liga 2
            'I2': '4558',   # Serie B
            'B1': '4330',   # Belgian Pro League
            'P1': '4344'    # Primeira Liga
        }
        
        # Takım ismi mapping (TheSportsDB -> CSV formatı) - TÜM LİGLER
        self.team_name_mappings = {
            # Premier League (E0)
            'Manchester City': 'Man City',
            'Manchester United': 'Man United',
            'Tottenham Hotspur': 'Tottenham',
            'Nottingham Forest': "Nott'm Forest",
            'Brighton and Hove Albion': 'Brighton',
            'West Ham United': 'West Ham',
            'Wolverhampton Wanderers': 'Wolves',
            'Leicester City': 'Leicester',
            'Ipswich Town': 'Ipswich',
            'AFC Bournemouth': 'Bournemouth',
            'Crystal Palace': 'Crystal Palace',
            'Newcastle United': 'Newcastle',
            'Aston Villa': 'Aston Villa',
            'Fulham': 'Fulham',
            'Chelsea': 'Chelsea',
            'Liverpool': 'Liverpool',
            'Arsenal': 'Arsenal',
            'Everton': 'Everton',
            'Brentford': 'Brentford',
            'Southampton': 'Southampton',
            
            # La Liga (SP1)
            'Real Madrid': 'Real Madrid',
            'FC Barcelona': 'Barcelona',
            'Atletico Madrid': 'Ath Madrid',
            'Athletic Bilbao': 'Ath Bilbao',
            'Real Betis': 'Betis',
            'Celta Vigo': 'Celta',
            'RCD Espanyol': 'Espanol',
            'Getafe CF': 'Getafe',
            'Girona FC': 'Girona',
            'UD Las Palmas': 'Las Palmas',
            'CD Leganes': 'Leganes',
            'RCD Mallorca': 'Mallorca',
            'CA Osasuna': 'Osasuna',
            'Sevilla FC': 'Sevilla',
            'Real Sociedad': 'Sociedad',
            'Valencia CF': 'Valencia',
            'Real Valladolid': 'Valladolid',
            'Rayo Vallecano': 'Vallecano',
            'Villarreal CF': 'Villarreal',
            'Deportivo Alaves': 'Alaves',
            
            # La Liga 2 (SP2)
            'Albacete Balompie': 'Albacete',
            'UD Almeria': 'Almeria',
            'Burgos CF': 'Burgos',
            'Cadiz CF': 'Cadiz',
            'FC Cartagena': 'Cartagena',
            'CD Castellon': 'Castellon',
            'Cordoba CF': 'Cordoba',
            'SD Eibar': 'Eibar',
            'Elche CF': 'Elche',
            'CD Eldense': 'Eldense',
            'Racing Ferrol': 'Ferrol',
            'Granada CF': 'Granada',
            'SD Huesca': 'Huesca',
            'RC Deportivo': 'La Coruna',
            'Levante UD': 'Levante',
            'Malaga CF': 'Malaga',
            'CD Mirandes': 'Mirandes',
            'Real Oviedo': 'Oviedo',
            'Racing Santander': 'Santander',
            'Sporting Gijon': 'Sp Gijon',
            'CD Tenerife': 'Tenerife',
            'Real Zaragoza': 'Zaragoza',
            
            # Bundesliga (D1)
            'FC Bayern Munich': 'Bayern Munich',
            'Borussia Dortmund': 'Dortmund',
            'Eintracht Frankfurt': 'Ein Frankfurt',
            'SC Freiburg': 'Freiburg',
            'FC Heidenheim': 'Heidenheim',
            'TSG Hoffenheim': 'Hoffenheim',
            'Holstein Kiel': 'Holstein Kiel',
            'Bayer Leverkusen': 'Leverkusen',
            'Borussia Monchengladbach': 'M\'gladbach',
            'Mainz 05': 'Mainz',
            'RB Leipzig': 'RB Leipzig',
            'FC St. Pauli': 'St Pauli',
            'VfB Stuttgart': 'Stuttgart',
            'Union Berlin': 'Union Berlin',
            'Werder Bremen': 'Werder Bremen',
            'VfL Wolfsburg': 'Wolfsburg',
            'FC Augsburg': 'Augsburg',
            'VfL Bochum': 'Bochum',
            
            # 2.Bundesliga (D2)
            'Eintracht Braunschweig': 'Braunschweig',
            'SV Darmstadt 98': 'Darmstadt',
            'SV Elversberg': 'Elversberg',
            'FC Koln': 'FC Koln',
            'Fortuna Dusseldorf': 'Fortuna Dusseldorf',
            'SpVgg Greuther Furth': 'Greuther Furth',
            'Hamburger SV': 'Hamburg',
            'Hannover 96': 'Hannover',
            'Hertha Berlin': 'Hertha',
            'FC Kaiserslautern': 'Kaiserslautern',
            'Karlsruher SC': 'Karlsruhe',
            'FC Magdeburg': 'Magdeburg',
            'FC Nurnberg': 'Nurnberg',
            'SC Paderborn': 'Paderborn',
            'Preußen Münster': 'Preußen Münster',
            'SSV Jahn Regensburg': 'Regensburg',
            'FC Schalke 04': 'Schalke 04',
            'SSV Ulm': 'Ulm',
            
            # Serie A (I1)
            'AC Milan': 'Milan',
            'Inter Milan': 'Inter',
            'Juventus': 'Juventus',
            'AS Roma': 'Roma',
            'SS Lazio': 'Lazio',
            'SSC Napoli': 'Napoli',
            'Atalanta': 'Atalanta',
            'ACF Fiorentina': 'Fiorentina',
            'Hellas Verona': 'Verona',
            'Bologna FC': 'Bologna',
            'Cagliari Calcio': 'Cagliari',
            'Como 1907': 'Como',
            'Empoli FC': 'Empoli',
            'Genoa CFC': 'Genoa',
            'US Lecce': 'Lecce',
            'AC Monza': 'Monza',
            'Parma Calcio': 'Parma',
            'Torino FC': 'Torino',
            'Udinese Calcio': 'Udinese',
            'Venezia FC': 'Venezia',
            
            # Serie B (I2)
            'FC Bari': 'Bari',
            'Brescia Calcio': 'Brescia',
            'Carrarese Calcio': 'Carrarese',
            'US Catanzaro': 'Catanzaro',
            'Cesena FC': 'Cesena',
            'AS Cittadella': 'Cittadella',
            'Cosenza Calcio': 'Cosenza',
            'US Cremonese': 'Cremonese',
            'Frosinone Calcio': 'Frosinone',
            'SS Juve Stabia': 'Juve Stabia',
            'Mantova FC': 'Mantova',
            'Modena FC': 'Modena',
            'Palermo FC': 'Palermo',
            'Pisa SC': 'Pisa',
            'AC Reggiana': 'Reggiana',
            'US Salernitana': 'Salernitana',
            'UC Sampdoria': 'Sampdoria',
            'US Sassuolo': 'Sassuolo',
            'Spezia Calcio': 'Spezia',
            'FC Sudtirol': 'Sudtirol',
            
            # Ligue 1 (F1)
            'Paris Saint-Germain': 'Paris SG',
            'Olympique Marseille': 'Marseille',
            'Olympique Lyon': 'Lyon',
            'AS Monaco': 'Monaco',
            'RC Lens': 'Lens',
            'Lille OSC': 'Lille',
            'OGC Nice': 'Nice',
            'Stade Rennais': 'Rennes',
            'RC Strasbourg': 'Strasbourg',
            'Toulouse FC': 'Toulouse',
            'Stade Brest': 'Brest',
            'Montpellier HSC': 'Montpellier',
            'FC Nantes': 'Nantes',
            'Stade Reims': 'Reims',
            'AS Saint-Etienne': 'St Etienne',
            'AJ Auxerre': 'Auxerre',
            'SCO Angers': 'Angers',
            'Le Havre AC': 'Le Havre',
            
            # Süper Lig (T1)
            'Galatasaray': 'Galatasaray',
            'Fenerbahce': 'Fenerbahce',
            'Besiktas': 'Besiktas',
            'Trabzonspor': 'Trabzonspor',
            'Adana Demirspor': 'Ad. Demirspor',
            'Alanyaspor': 'Alanyaspor',
            'Antalyaspor': 'Antalyaspor',
            'Bodrumspor': 'Bodrumspor',
            'Istanbul Basaksehir': 'Buyuksehyr',
            'Eyupspor': 'Eyupspor',
            'Gaziantep FK': 'Gaziantep',
            'Goztepe': 'Goztep',
            'Hatayspor': 'Hatayspor',
            'Kasimpasa': 'Kasimpasa',
            'Kayserispor': 'Kayserispor',
            'Konyaspor': 'Konyaspor',
            'Caykur Rizespor': 'Rizespor',
            'Samsunspor': 'Samsunspor',
            'Sivasspor': 'Sivasspor',
            
            # Jupiler Pro League (B1)
            'RSC Anderlecht': 'Anderlecht',
            'Royal Antwerp FC': 'Antwerp',
            'Beerschot VA': 'Beerschot VA',
            'Cercle Brugge': 'Cercle Brugge',
            'Sporting Charleroi': 'Charleroi',
            'Club Brugge': 'Club Brugge',
            'FCV Dender EH': 'Dender',
            'KRC Genk': 'Genk',
            'KAA Gent': 'Gent',
            'KV Kortrijk': 'Kortrijk',
            'KV Mechelen': 'Mechelen',
            'OH Leuven': 'Oud-Heverlee Leuven',
            'Sint-Truidense VV': 'St Truiden',
            'Union Saint-Gilloise': 'St. Gilloise',
            'Standard Liege': 'Standard',
            'KVC Westerlo': 'Westerlo',
            
            # Primeira Liga (P1)
            'SL Benfica': 'Benfica',
            'FC Porto': 'Porto',
            'Sporting CP': 'Sp Lisbon',
            'SC Braga': 'Sp Braga',
            'Vitoria Guimaraes': 'Guimaraes',
            'Boavista FC': 'Boavista',
            'Moreirense FC': 'Moreirense',
            'Gil Vicente FC': 'Gil Vicente',
            'Rio Ave FC': 'Rio Ave',
            'FC Arouca': 'Arouca',
            'CD Santa Clara': 'Santa Clara',
            'Estoril Praia': 'Estoril',
            'CF Estrela': 'Estrela',
            'FC Famalicao': 'Famalicao',
            'SC Farense': 'Farense',
            'CD Nacional': 'Nacional',
            'Casa Pia AC': 'Casa Pia',
            'AVS Futebol SAD': 'AVS'
        }
    
    def map_team_name(self, api_name):
        """API'deki takım ismini CSV formatına çevir"""
        return self.team_name_mappings.get(api_name, api_name)
    
    def get_today_fixtures(self, league_code):
        """SADECE bugünün maçlarını al - yoksa boş liste döndür"""
        try:
            league_id = self.league_mappings.get(league_code)
            if not league_id:
                print(f"⚠️ {league_code} için league ID bulunamadı")
                return []
            
            # Bugünün tarihi
            today = datetime.now().strftime('%Y-%m-%d')
            
            # TheSportsDB fixture endpoint
            url = f"{self.base_url}/eventsday.php"
            params = {
                'd': today,
                'l': league_id
            }
            
            print(f"🔍 {league_code} için {today} tarihindeki maçlar kontrol ediliyor...")
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ TheSportsDB API hatası: {response.status_code}")
                return []
            
            data = response.json()
            
            # Maç yoksa boş liste döndür
            if not data.get('events'):
                print(f"❌ {league_code} için bugün maç yok")
                return []
            
            fixtures = []
            for event in data['events'][:3]:  # Max 3 maç
                home_team_api = event.get('strHomeTeam', '')
                away_team_api = event.get('strAwayTeam', '')
                match_time = event.get('strTime', '15:00')
                
                # Takım isimlerini CSV formatına çevir
                home_team = self.map_team_name(home_team_api)
                away_team = self.map_team_name(away_team_api)
                
                # Saat formatını düzenle
                if match_time and ':' in match_time:
                    time_formatted = match_time[:5]  # "15:00:00" -> "15:00"
                else:
                    time_formatted = "15:00"
                
                fixtures.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': today,
                    'time': time_formatted,
                    'league': f"Live {league_code}",
                    'source': 'sportsdb',
                    'api_home': home_team_api,
                    'api_away': away_team_api
                })
            
            print(f"✅ {league_code} için {len(fixtures)} maç bulundu")
            return fixtures
            
        except Exception as e:
            print(f"❌ SportsDB fetch hatası: {e}")
            return []

# Test
if __name__ == "__main__":
    fetcher = SportsDBFetcher()
    
    # Test tüm ligler
    test_leagues = ['E0', 'SP1', 'D1', 'I1', 'T1', 'F1', 'D2', 'SP2', 'I2', 'B1', 'P1']
    league_names = [
        'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Süper Lig', 
        'Ligue 1', '2.Bundesliga', 'La Liga 2', 'Serie B', 'Jupiler Pro League', 'Primeira Liga'
    ]
    
    print("🏆 TÜM LİGLER İÇİN FIXTURE KONTROL")
    print("=" * 50)
    
    for league, name in zip(test_leagues, league_names):
        print(f"\n🏆 {name} ({league}):")
        fixtures = fetcher.get_today_fixtures(league)
        
        if fixtures:
            for fixture in fixtures:
                print(f"  ⚽ {fixture['home_team']} vs {fixture['away_team']} - {fixture['time']}")
                print(f"     API: {fixture['api_home']} vs {fixture['api_away']}")
        else:
            print(f"  📅 Bugün maç yok")
    
    print(f"\n🎉 Tüm 11 lig fixture sistemi hazır!")