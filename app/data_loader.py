import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    
    def __init__(self, data_path="data/KHL_v1.csv"):
        self.data_path = data_path
        self.df = None
        self.teams = []
        self.seasons = []
    
    def load(self):
        try:
            self.df = pd.read_csv(self.data_path)
            
            self.df['SCORE'] = self.df['HG'].astype(str) + ':' + self.df['AG'].astype(str)
            
            self._get_metadata()
            logger.info(f"Данные загружены: {len(self.df)} строк, создана колонка SCORE")
            return True
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False
    
    def _get_metadata(self):
        home_teams = self.df['HOMETEAM'].unique()
        away_teams = self.df['AWAYTEAM'].unique()

        all_teams_set = set(home_teams) | set(away_teams)
        self.teams = sorted(all_teams_set)

        if len(set(home_teams)) != len(set(away_teams)):
            logger.warning(f"Разное количество домашних ({len(set(home_teams))}) и гостевых ({len(set(away_teams))}) команд")

        self.seasons = sorted(self.df['SEASON'].unique())
    
    def get_team_stats(self, team_name):
        if self.df is None:
            return {}
        
        games = self.df[
            (self.df['HOMETEAM'] == team_name) | 
            (self.df['AWAYTEAM'] == team_name)
        ]
        
        if len(games) == 0:
            return {}
        
        wins = len(games[games['WINNER'] == team_name])
        total = len(games)
        
        return {
            'team': team_name,
            'games': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': f"{(wins/total*100):.1f}%"
        }

loader = DataLoader()