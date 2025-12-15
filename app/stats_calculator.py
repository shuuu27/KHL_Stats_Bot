import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import time
from app.simple_cache import get_from_cache, save_to_cache, make_cache_key, cleanup_expired

class StatsCalculator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        print(f"📊 StatsCalculator инициализирован с {len(df)} записями")
    
    def _get_team_stats_cached(self, team_name: str, season_id: Optional[str] = None) -> Dict:
        cache_key = make_cache_key("team_stats", team_name, season_id or "all")
        cached_result = get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        print(f"🔍 РАСЧЕТ: статистика {team_name} {season_id or 'all seasons'}")
        calc_start = time.time()
        
        if season_id and season_id != "all":
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        else:
            df_filtered = self.df
        
        df_our_team = df_filtered[
            (df_filtered['HOMETEAM'] == team_name) | 
            (df_filtered['AWAYTEAM'] == team_name)
        ].copy()
        
        if len(df_our_team) == 0:
            result = {}
        else:
            df_our_team['LOSER'] = df_our_team.apply(
                lambda row: row['AWAYTEAM'] if row['WINNER'] == row['HOMETEAM'] else row['HOMETEAM'],
                axis=1
            )
            
            df_our_team['POINTS'] = df_our_team.apply(
                lambda row: 3 if row['WINNER'] == team_name and pd.isna(row['ADD'])
                else 2 if row['WINNER'] == team_name and row['ADD'] in ['AOT', 'PEN']
                else 1 if row['WINNER'] != team_name and row['ADD'] in ['AOT', 'PEN']
                else 0,
                axis=1
            )
            
            df_our_team['GOALS'] = df_our_team.apply(
                lambda row: row['HG'] if row['HOMETEAM'] == team_name else row['AG'],
                axis=1
            )
            
            df_our_team['MISSED'] = df_our_team.apply(
                lambda row: row['AG'] if row['HOMETEAM'] == team_name else row['HG'],
                axis=1
            )
            
            scored_goals = df_our_team['GOALS'].sum()
            missed_goals = df_our_team['MISSED'].sum()
            wins = len(df_our_team[df_our_team['WINNER'] == team_name])
            total = len(df_our_team)
            points = df_our_team['POINTS'].sum()
            
            if total == 0:
                result = {
                    'team': team_name,
                    'games': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_rate': "0.0%",
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'goal_difference': 0,
                    'points': 0,
                    'avg_goals_per_game': "0.0",
                    'avg_conceded_per_game': "0.0"
                }
            else:
                result = {
                    'team': team_name,
                    'games': total,
                    'wins': wins,
                    'losses': total - wins,
                    'win_rate': f"{(wins/total*100):.1f}%",
                    'goals_scored': int(scored_goals),
                    'goals_conceded': int(missed_goals),
                    'goal_difference': int(scored_goals - missed_goals),
                    'points': int(points),
                    'avg_goals_per_game': f"{(scored_goals/total):.1f}",
                    'avg_conceded_per_game': f"{(missed_goals/total):.1f}",
                    'cached': False
                }
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        calc_time = (time.time() - calc_start) * 1000
        print(f"✅ РАССЧИТАНО: {team_name} за {calc_time:.1f} мс")
        return result
    
    def get_team_stats(self, team_name: str, season_id: Optional[str] = None) -> Dict:
        return self._get_team_stats_cached(team_name, season_id)
    
    def get_head_to_head(self, team1: str, team2: str, season_id: Optional[str] = None) -> Dict:
        cache_key = make_cache_key("h2h", team1, team2, season_id or "all")
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ H2H: {team1} vs {team2} {season_id or 'all seasons'}")
        calc_start = time.time()
        
        if season_id and season_id != "all":
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        else:
            df_filtered = self.df
        
        df_games = df_filtered[
            ((df_filtered['HOMETEAM'] == team1) & (df_filtered['AWAYTEAM'] == team2)) |
            ((df_filtered['HOMETEAM'] == team2) & (df_filtered['AWAYTEAM'] == team1))
        ]
        
        if len(df_games) == 0:
            result = {}
        else:
            team1_wins = len(df_games[df_games['WINNER'] == team1])
            team2_wins = len(df_games[df_games['WINNER'] == team2])
            total = len(df_games)
            
            
            games_list = []
            for _, row in df_games.iterrows():
                
                if row['HOMETEAM'] == team1:
                    home_team = team1
                    away_team = team2
                    home_score = row['HG']
                    away_score = row['AG']
                else:
                    home_team = team2
                    away_team = team1
                    home_score = row['HG']
                    away_score = row['AG']
                
                
                score = f"{home_score}:{away_score}"
                
                games_list.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'score': score,
                    'winner': row['WINNER']
                })
            
            result = {
                'team1': team1,
                'team2': team2,
                'total_games': total,
                'team1_wins': team1_wins,
                'team2_wins': team2_wins,
                'team1_winrate': f"{(team1_wins/total*100):.1f}%" if total > 0 else "0.0%",
                'team2_winrate': f"{(team2_wins/total*100):.1f}%" if total > 0 else "0.0%",
                'games': games_list,
                'cached': False
            }
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        calc_time = (time.time() - calc_start) * 1000
        print(f"✅ РАССЧИТАНО H2H за {calc_time:.1f} мс")
        return result
    
    def get_home_stats(self, team_name: str, season_id: Optional[str] = None) -> Dict:
        cache_key = make_cache_key("home_stats", team_name, season_id or "all")
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ домашней статистики: {team_name} {season_id or 'all seasons'}")
        
        if season_id and season_id != "all":
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        else:
            df_filtered = self.df
        
        home_games = df_filtered[df_filtered['HOMETEAM'] == team_name].copy()
        
        if len(home_games) == 0:
            result = {}
        else:
            home_games['POINTS'] = home_games.apply(
                lambda row: 3 if row['WINNER'] == team_name and pd.isna(row['ADD'])
                else 2 if row['WINNER'] == team_name and row['ADD'] in ['AOT', 'PEN']
                else 1 if row['WINNER'] != team_name and row['ADD'] in ['AOT', 'PEN']
                else 0,
                axis=1
            )
            
            wins = len(home_games[home_games['WINNER'] == team_name])
            total = len(home_games)
            points = home_games['POINTS'].sum()
            goals_scored = home_games['HG'].sum()
            goals_conceded = home_games['AG'].sum()
            
            if total == 0:
                result = {
                    'team': team_name,
                    'games': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_rate': "0.0%",
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'goal_difference': 0,
                    'points': 0,
                    'avg_goals_per_game': "0.0",
                    'avg_conceded_per_game': "0.0"
                }
            else:
                result = {
                    'team': team_name,
                    'games': total,
                    'wins': wins,
                    'losses': total - wins,
                    'win_rate': f"{(wins/total*100):.1f}%",
                    'goals_scored': int(goals_scored),
                    'goals_conceded': int(goals_conceded),
                    'goal_difference': int(goals_scored - goals_conceded),
                    'points': int(points),
                    'avg_goals_per_game': f"{(goals_scored/total):.1f}",
                    'avg_conceded_per_game': f"{(goals_conceded/total):.1f}",
                    'cached': False
                }
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result
    
    def get_away_stats(self, team_name: str, season_id: Optional[str] = None) -> Dict:
        cache_key = make_cache_key("away_stats", team_name, season_id or "all")
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ гостевой статистики: {team_name} {season_id or 'all seasons'}")
        
        if season_id and season_id != "all":
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        else:
            df_filtered = self.df
        
        away_games = df_filtered[df_filtered['AWAYTEAM'] == team_name].copy()
        
        if len(away_games) == 0:
            result = {}
        else:
            away_games['POINTS'] = away_games.apply(
                lambda row: 3 if row['WINNER'] == team_name and pd.isna(row['ADD'])
                else 2 if row['WINNER'] == team_name and row['ADD'] in ['AOT', 'PEN']
                else 1 if row['WINNER'] != team_name and row['ADD'] in ['AOT', 'PEN']
                else 0,
                axis=1
            )
            
            wins = len(away_games[away_games['WINNER'] == team_name])
            total = len(away_games)
            points = away_games['POINTS'].sum()
            goals_scored = away_games['AG'].sum()
            goals_conceded = away_games['HG'].sum()
            
            if total == 0:
                result = {
                    'team': team_name,
                    'games': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_rate': "0.0%",
                    'goals_scored': 0,
                    'goals_conceded': 0,
                    'goal_difference': 0,
                    'points': 0,
                    'avg_goals_per_game': "0.0",
                    'avg_conceded_per_game': "0.0"
                }
            else:
                result = {
                    'team': team_name,
                    'games': total,
                    'wins': wins,
                    'losses': total - wins,
                    'win_rate': f"{(wins/total*100):.1f}%",
                    'goals_scored': int(goals_scored),
                    'goals_conceded': int(goals_conceded),
                    'goal_difference': int(goals_scored - goals_conceded),
                    'points': int(points),
                    'avg_goals_per_game': f"{(goals_scored/total):.1f}",
                    'avg_conceded_per_game': f"{(goals_conceded/total):.1f}",
                    'cached': False
                }
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result
    
    def get_last_games(self, team_name: str, n_games: int = 10) -> List[Dict]:
        cache_key = make_cache_key("last_games", team_name, n_games)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ последних игр: {team_name} ({n_games} игр)")
        
        if 'DATE' not in self.df.columns:
            result = []
        else:
            team_games = self.df[
                (self.df['HOMETEAM'] == team_name) | 
                (self.df['AWAYTEAM'] == team_name)
            ].copy()
            
            if len(team_games) == 0:
                result = []
            else:
                team_games['DATE'] = pd.to_datetime(team_games['DATE'])
                team_games = team_games.sort_values('DATE', ascending=False).head(n_games)
                
                formatted_games = []
                for _, row in team_games.iterrows():
                    # Создаем счёт из HG и AG
                    score = f"{row['HG']}:{row['AG']}"
                    game = {
                        'date': row['DATE'].strftime('%d.%m.%Y'),
                        'home_team': row['HOMETEAM'],
                        'away_team': row['AWAYTEAM'],
                        'score': score,
                        'winner': row['WINNER'],
                        'is_home': row['HOMETEAM'] == team_name
                    }
                    formatted_games.append(game)
                result = formatted_games
        
        save_to_cache(cache_key, result, ttl_seconds=600)
        return result
    
    def get_form_stats(self, team_name: str, n_games: int = 10) -> Dict:
        cache_key = make_cache_key("form_stats", team_name, n_games)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ формы: {team_name} ({n_games} игр)")
        
        last_games = self.get_last_games(team_name, n_games)
        
        if not last_games:
            result = {}
        else:
            wins = sum(1 for game in last_games if game['winner'] == team_name)
            total = len(last_games)
            
            result = {
                'team': team_name,
                'games': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': f"{(wins/total*100):.1f}%" if total > 0 else "0.0%",
                'last_games': last_games,
                'cached': False
            }
        
        save_to_cache(cache_key, result, ttl_seconds=600)
        return result
    
    def get_season_table(self, season_id: str) -> List[Dict]:
        cache_key = make_cache_key("season_table", season_id)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ таблицы сезона: {season_id}")
        calc_start = time.time()
        
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        if len(df_filtered) == 0:
            result = []
        else:
            df_for_table = df_filtered[['HOMETEAM', 'AWAYTEAM', 'WINNER', 'ADD', 'HG', 'AG']].copy()
            
            df_for_table['HOMEPOINTS'] = df_for_table.apply(
                lambda row: 3 if row['HOMETEAM'] == row['WINNER'] and pd.isna(row['ADD'])
                else 2 if row['HOMETEAM'] == row['WINNER']
                else 0 if row['HOMETEAM'] != row['WINNER'] and pd.isna(row['ADD'])
                else 1, axis=1
            )
            df_for_table['AWAYPOINTS'] = 3 - df_for_table['HOMEPOINTS']
            
            home_stats = df_for_table.groupby('HOMETEAM').agg({
                'HOMETEAM': 'count',
                'ADD': lambda x: (x.notna()).sum(),
                'HOMEPOINTS': 'sum',
                'WINNER': lambda x: (x == df_for_table.loc[x.index, 'HOMETEAM']).sum(),
                'HG': 'sum',
                'AG': 'sum'
            }).rename(columns={
                'HOMETEAM': 'GAMES',
                'HOMEPOINTS': 'POINTS',
                'WINNER': 'WINS',
                'ADD': 'OT_LOSSES'
            })
            
            away_stats = df_for_table.groupby('AWAYTEAM').agg({
                'AWAYTEAM': 'count',
                'ADD': lambda x: (x.notna()).sum(),
                'AWAYPOINTS': 'sum',
                'WINNER': lambda x: (x == df_for_table.loc[x.index, 'AWAYTEAM']).sum(),
                'AG': 'sum',
                'HG': 'sum'
            }).rename(columns={
                'AWAYTEAM': 'GAMES',
                'AWAYPOINTS': 'POINTS',
                'WINNER': 'WINS',
                'ADD': 'OT_LOSSES'
            })
            
            total_stats = home_stats.add(away_stats, fill_value=0).astype(int)
            
            if total_stats.index.name is not None:
                total_stats = total_stats.reset_index().rename(columns={total_stats.index.name: "TEAM"})
            else:
                total_stats = total_stats.reset_index().rename(columns={"index": "TEAM"})
            
            table_data = []
            for i, (_, row) in enumerate(total_stats.iterrows(), 1):
                ot_losses = row['OT_LOSSES']
                regular_losses = row['GAMES'] - row['WINS'] - ot_losses
                goals_for = int(row['HG'])
                goals_against = int(row['AG'])
                goal_diff = goals_for - goals_against
                
                table_data.append({
                    'place': i,
                    'team': row['TEAM'],
                    'games': int(row['GAMES']),
                    'wins': int(row['WINS']),
                    'ot_losses': int(ot_losses),
                    'regular_losses': int(regular_losses),
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'goal_diff': goal_diff,
                    'points': int(row['POINTS'])
                })
            
            result = sorted(table_data, key=lambda x: x['points'], reverse=True)
        
        save_to_cache(cache_key, result, ttl_seconds=3600)
        calc_time = (time.time() - calc_start) * 1000
        print(f"✅ РАССЧИТАНА таблица сезона {season_id} за {calc_time:.1f} мс")
        return result
    
    def get_top_winners(self, season_id: str = "all", limit: int = 10) -> List[Dict]:
        cache_key = make_cache_key("top_winners", season_id, limit)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ топ-{limit} по победам: {season_id}")
        
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        if len(df_filtered) == 0:
            result = []
        else:
            wins_df = df_filtered['WINNER'].value_counts().reset_index()
            wins_df.columns = ['team', 'wins']
            
            top_winners = []
            for i, (_, row) in enumerate(wins_df.head(limit).iterrows(), 1):
                top_winners.append({
                    'place': i,
                    'team': row['team'],
                    'wins': int(row['wins'])
                })
            
            result = top_winners
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result
    
    def get_top_points(self, season_id: str = "all", limit: int = 10) -> List[Dict]:
        cache_key = make_cache_key("top_points", season_id, limit)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ топ-{limit} по очкам: {season_id}")
        
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        if len(df_filtered) == 0:
            result = []
        else:
            df_for_table = df_filtered[['HOMETEAM', 'AWAYTEAM', 'WINNER', 'ADD', 'HG', 'AG']].copy()
            
            df_for_table['HOMEPOINTS'] = df_for_table.apply(
                lambda row: 3 if row['HOMETEAM'] == row['WINNER'] and pd.isna(row['ADD'])
                else 2 if row['HOMETEAM'] == row['WINNER']
                else 0 if row['HOMETEAM'] != row['WINNER'] and pd.isna(row['ADD'])
                else 1, axis=1
            )
            df_for_table['AWAYPOINTS'] = 3 - df_for_table['HOMEPOINTS']
            
            home_stats = df_for_table.groupby('HOMETEAM').agg({
                'HOMEPOINTS': 'sum',
            })
            away_stats = df_for_table.groupby('AWAYTEAM').agg({
                'AWAYPOINTS': 'sum',
            })
            
            home_stats = home_stats.rename(columns={'HOMEPOINTS': 'POINTS'})
            away_stats = away_stats.rename(columns={'AWAYPOINTS': 'POINTS'})
            
            total_stats = home_stats.add(away_stats, fill_value=0).astype(int)
            total_stats = total_stats.sort_values('POINTS', ascending=False)
            
            top_points = []
            for i, (team, points) in enumerate(total_stats.head(limit).iterrows(), 1):
                top_points.append({
                    'place': i,
                    'team': team,
                    'points': int(points['POINTS'])
                })
            
            result = top_points
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result
    
    def get_top_winrate(self, season_id: str = "all", min_games: int = 10, limit: int = 10) -> List[Dict]:
        cache_key = make_cache_key("top_winrate", season_id, min_games, limit)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ топ-{limit} по проценту побед: {season_id}")
        
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        if len(df_filtered) == 0:
            result = []
        else:
            df_wr = df_filtered[['HOMETEAM', 'AWAYTEAM', 'WINNER']].copy()
            df_wr['LOSER'] = df_wr.apply(
                lambda row: row['AWAYTEAM'] if row['WINNER'] == row['HOMETEAM'] else row['HOMETEAM'],
                axis=1
            )
            
            wins_count = df_wr['WINNER'].value_counts()
            lost_count = df_wr['LOSER'].value_counts()
            
            winrate_df = pd.DataFrame({
                'WINS': wins_count,
                'LOSSES': lost_count
            }).fillna(0)
            
            winrate_df['TOTAL'] = winrate_df['WINS'] + winrate_df['LOSSES']
            winrate_df = winrate_df[winrate_df['TOTAL'] >= min_games]
            
            winrate_df['WINRATE'] = (winrate_df['WINS'] / winrate_df['TOTAL'] * 100).round(1)
            winrate_df = winrate_df.sort_values('WINRATE', ascending=False)
            
            top_winrate = []
            for i, (team, row) in enumerate(winrate_df.head(limit).iterrows(), 1):
                top_winrate.append({
                    'place': i,
                    'team': team,
                    'wins': int(row['WINS']),
                    'losses': int(row['LOSSES']),
                    'total': int(row['TOTAL']),
                    'winrate': float(row['WINRATE'])
                })
            
            result = top_winrate
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result
    
    def get_top_goal_scorers(self, season_id: str = "all", limit: int = 10) -> List[Dict]:
        cache_key = make_cache_key("top_scorers", season_id, limit)
        cached = get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        print(f"🔍 РАСЧЕТ топ-{limit} по забитым голам: {season_id}")
        
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        if len(df_filtered) == 0:
            result = []
        else:
            df_for_table = df_filtered[['HOMETEAM', 'AWAYTEAM', 'HG', 'AG']].copy()
            
            home_goals = df_for_table.groupby('HOMETEAM')['HG'].sum()
            away_goals = df_for_table.groupby('AWAYTEAM')['AG'].sum()
            
            total_goals = home_goals.add(away_goals, fill_value=0).astype(int)
            total_goals = total_goals.sort_values(ascending=False)
            
            top_scorers = []
            for i, (team, goals) in enumerate(total_goals.head(limit).items(), 1):
                top_scorers.append({
                    'place': i,
                    'team': team,
                    'goals': int(goals)
                })
            
            result = top_scorers
        
        save_to_cache(cache_key, result, ttl_seconds=1800)
        return result