import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.model = None
        self.le = None
        self.team_stats = None
        self.feature_columns = None
        self._prepare_data()
        self._train_model()
    
    def _prepare_data(self):
 
        df_preds = self.df[['HOMETEAM', 'AWAYTEAM', 'WINNER', 'HG', 'AG', 'ADD', 'SEASON']].copy()
        

        self.team_stats = {}
        
        for team in pd.concat([df_preds['HOMETEAM'], df_preds['AWAYTEAM']]).unique():
            home_games = df_preds[df_preds['HOMETEAM'] == team]
            away_games = df_preds[df_preds['AWAYTEAM'] == team]
            
            total_games = len(home_games) + len(away_games)
            
            if total_games > 0:
                home_win_rate = len(home_games[home_games['WINNER'] == team]) / len(home_games) if len(home_games) > 0 else 0
                away_win_rate = len(away_games[away_games['WINNER'] == team]) / len(away_games) if len(away_games) > 0 else 0
                overall_win_rate = (len(home_games[home_games['WINNER'] == team]) + len(away_games[away_games['WINNER'] == team])) / total_games
                
                self.team_stats[team] = {
                    'home_win_rate': home_win_rate,
                    'away_win_rate': away_win_rate,
                    'overall_win_rate': overall_win_rate,
                    'total_games': total_games
                }
            else:
                self.team_stats[team] = {'home_win_rate': 0, 'away_win_rate': 0, 'overall_win_rate': 0, 'total_games': 0}
        

        df_preds['HOME_WIN_RATE'] = df_preds['HOMETEAM'].map(lambda x: self.team_stats[x]['home_win_rate'])
        df_preds['AWAY_WIN_RATE'] = df_preds['AWAYTEAM'].map(lambda x: self.team_stats[x]['away_win_rate'])
        df_preds['HOME_OVERALL_RATE'] = df_preds['HOMETEAM'].map(lambda x: self.team_stats[x]['overall_win_rate'])
        df_preds['AWAY_OVERALL_RATE'] = df_preds['AWAYTEAM'].map(lambda x: self.team_stats[x]['overall_win_rate'])
        

        self.le = LabelEncoder()
        all_teams = pd.concat([df_preds['HOMETEAM'], df_preds['AWAYTEAM']]).unique()
        self.le.fit(all_teams)
        
        df_preds['HOME_TEAM_ENCODED'] = self.le.transform(df_preds['HOMETEAM'])
        df_preds['AWAY_TEAM_ENCODED'] = self.le.transform(df_preds['AWAYTEAM'])
        

        def get_winner_code(row):
            if row['WINNER'] == row['HOMETEAM']:
                return 1  
            elif row['WINNER'] == row['AWAYTEAM']:
                return 0
            else:
                return 2
        
        df_preds['WINNER_CODE'] = df_preds.apply(get_winner_code, axis=1)
        
        self.feature_columns = [
            'HOME_TEAM_ENCODED', 'AWAY_TEAM_ENCODED',
            'HOME_WIN_RATE', 'AWAY_WIN_RATE',
            'HOME_OVERALL_RATE', 'AWAY_OVERALL_RATE'
        ]
        
        self.df_processed = df_preds
    
    def _train_model(self):

        X = self.df_processed[self.feature_columns]
        y = self.df_processed['WINNER_CODE']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=21, stratify=y
        )

        self.model = RandomForestClassifier(n_estimators=100, random_state=21)
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Модель обучена. Точность: {accuracy:.2%}")
    
    def predict_match(self, home_team: str, away_team: str) -> Dict:

        if home_team not in self.team_stats or away_team not in self.team_stats:
            return {"error": "Одна из команд не найдена в базе данных"}
        
        if home_team == away_team:
            return {"error": "Команды не могут быть одинаковыми"}
        

        home_encoded = self.le.transform([home_team])[0]
        away_encoded = self.le.transform([away_team])[0]
        
        home_win_rate = self.team_stats.get(home_team, {}).get('home_win_rate', 0)
        away_win_rate = self.team_stats.get(away_team, {}).get('away_win_rate', 0)
        home_overall = self.team_stats.get(home_team, {}).get('overall_win_rate', 0)
        away_overall = self.team_stats.get(away_team, {}).get('overall_win_rate', 0)
        
        prediction_data = pd.DataFrame([{
            'HOME_TEAM_ENCODED': home_encoded,
            'AWAY_TEAM_ENCODED': away_encoded,
            'HOME_WIN_RATE': home_win_rate,
            'AWAY_WIN_RATE': away_win_rate,
            'HOME_OVERALL_RATE': home_overall,
            'AWAY_OVERALL_RATE': away_overall
        }])
        

        prediction = self.model.predict(prediction_data)[0]
        probabilities = self.model.predict_proba(prediction_data)[0]

        result_map = {
            0: {"result": "away_win", "description": f"Победа {away_team}"},
            1: {"result": "home_win", "description": f"Победа {home_team}"},
            2: {"result": "draw", "description": "Ничья"}
        }

        prob_map = {}
        for i, class_idx in enumerate(self.model.classes_):
            if class_idx == 0:
                prob_map["away_win"] = float(probabilities[i])
            elif class_idx == 1:
                prob_map["home_win"] = float(probabilities[i])
            elif class_idx == 2:
                prob_map["draw"] = float(probabilities[i])
        
        return {
            "home_team": home_team,
            "away_team": away_team,
            "prediction": result_map[prediction],
            "probabilities": prob_map,
            "team_stats": {
                "home": self.team_stats[home_team],
                "away": self.team_stats[away_team]
            }
        }
    
    def get_head_to_head_stats(self, team1: str, team2: str) -> Dict:

        df_games = self.df[
            ((self.df['HOMETEAM'] == team1) & (self.df['AWAYTEAM'] == team2)) |
            ((self.df['HOMETEAM'] == team2) & (self.df['AWAYTEAM'] == team1))
        ]
        
        if len(df_games) == 0:
            return {"total_games": 0}
        
        team1_wins = len(df_games[df_games['WINNER'] == team1])
        team2_wins = len(df_games[df_games['WINNER'] == team2])
        total = len(df_games)
        
        return {
            "total_games": total,
            f"{team1}_wins": team1_wins,
            f"{team2}_wins": team2_wins,
            f"{team1}_winrate": team1_wins / total if total > 0 else 0,
            f"{team2}_winrate": team2_wins / total if total > 0 else 0,
            "last_games": df_games[['HOMETEAM', 'AWAYTEAM', 'SCORE', 'WINNER']].tail(5).to_dict('records')
        }