import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from io import BytesIO
from typing import List, Dict, Optional

# Настройки для Telegram
plt.style.use('seaborn-v0_8-darkgrid')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['figure.figsize'] = (10, 6)
matplotlib.rcParams['figure.dpi'] = 100

class PlotGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def create_top_winners_plot(self, season_id: str = "all", top_n: int = 10) -> BytesIO:
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        wins_df = pd.DataFrame(df_filtered['WINNER'].value_counts()).reset_index()
        wins_df.columns = ['team', 'wins']
        wins_df = wins_df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.Greens_r(np.linspace(0.2, 0.7, len(wins_df)))
        
        bars = ax.barh(wins_df['team'], wins_df['wins'], color=colors, alpha=0.8)
        ax.set_xlabel('Количество побед', fontsize=12)
        ax.set_title(f'Топ-{top_n} команд по победам', fontsize=14, fontweight='bold', pad=20)
        
        for i, (bar, wins) in enumerate(zip(bars, wins_df['wins'])):
            ax.text(wins + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{wins}', ha='left', va='center', fontweight='bold')
        
        ax.invert_yaxis()
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def create_top_points_plot(self, season_id: str = "all", top_n: int = 10) -> BytesIO:
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        df_for_table = df_filtered[['HOMETEAM', 'AWAYTEAM', 'WINNER', 'ADD']].copy()
        
        df_for_table['HOMEPOINTS'] = df_for_table.apply(
            lambda row: 3 if row['HOMETEAM'] == row['WINNER'] and pd.isna(row['ADD'])
            else 2 if row['HOMETEAM'] == row['WINNER']
            else 0 if row['HOMETEAM'] != row['WINNER'] and pd.isna(row['ADD'])
            else 1, axis=1
        )
        df_for_table['AWAYPOINTS'] = 3 - df_for_table['HOMEPOINTS']
        
        home_stats = df_for_table.groupby('HOMETEAM')['HOMEPOINTS'].sum()
        away_stats = df_for_table.groupby('AWAYTEAM')['AWAYPOINTS'].sum()
        
        total_stats = home_stats.add(away_stats, fill_value=0).astype(int)
        total_stats = total_stats.sort_values(ascending=False).head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.Blues_r(np.linspace(0.2, 0.7, len(total_stats)))
        
        bars = ax.barh(total_stats.index, total_stats.values, color=colors, alpha=0.8)
        ax.set_xlabel('Очки', fontsize=12)
        ax.set_title(f'Топ-{top_n} команд по очкам', fontsize=14, fontweight='bold', pad=20)
        
        for i, (bar, points) in enumerate(zip(bars, total_stats.values)):
            ax.text(points + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{points}', ha='left', va='center', fontweight='bold')
        
        ax.invert_yaxis()
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def create_team_form_plot(self, team_name: str, n_games: int = 10) -> BytesIO:
        team_games = self.df[
            (self.df['HOMETEAM'] == team_name) | 
            (self.df['AWAYTEAM'] == team_name)
        ].copy()
        
        if len(team_games) == 0:
            return None
        
        team_games['DATE'] = pd.to_datetime(team_games['DATE'])
        team_games = team_games.sort_values('DATE', ascending=True).tail(n_games)
        
        results = []
        for _, row in team_games.iterrows():
            if row['WINNER'] == team_name:
                results.append(3)  # Победа
            elif pd.isna(row['ADD']):
                results.append(0)  # Поражение
            else:
                results.append(1)  # Поражение в OT/SO
        
        games_numbers = list(range(1, len(results) + 1))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = []
        for result in results:
            if result == 3:
                colors.append('#2ecc71')  # Зеленый - победа
            elif result == 1:
                colors.append('#f39c12')  # Оранжевый - OT поражение
            else:
                colors.append('#e74c3c')  # Красный - поражение
        
        bars = ax.bar(games_numbers, results, color=colors, alpha=0.8, edgecolor='black')
        ax.set_xlabel('Последние игры', fontsize=12)
        ax.set_ylabel('Очки', fontsize=12)
        ax.set_title(f'Форма команды {team_name} (последние {n_games} игр)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xticks(games_numbers)
        ax.set_ylim(0, 3.5)
        ax.grid(True, alpha=0.3)
        
        legend_elements = [
            plt.Rectangle((0,0),1,1, color='#2ecc71', alpha=0.8, label='Победа (3 очка)'),
            plt.Rectangle((0,0),1,1, color='#f39c12', alpha=0.8, label='Поражение в OT (1 очко)'),
            plt.Rectangle((0,0),1,1, color='#e74c3c', alpha=0.8, label='Поражение (0 очков)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def create_goals_comparison_plot(self, team1: str, team2: str, season_id: str = "all") -> BytesIO:
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        team1_home = df_filtered[df_filtered['HOMETEAM'] == team1]['HG'].sum()
        team1_away = df_filtered[df_filtered['AWAYTEAM'] == team1]['AG'].sum()
        team1_total = team1_home + team1_away
        
        team2_home = df_filtered[df_filtered['HOMETEAM'] == team2]['HG'].sum()
        team2_away = df_filtered[df_filtered['AWAYTEAM'] == team2]['AG'].sum()
        team2_total = team2_home + team2_away
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # График 1: Общее количество голов
        teams = [team1[:15], team2[:15]]
        totals = [team1_total, team2_total]
        
        colors = ['#3498db', '#e74c3c']
        bars1 = ax1.bar(teams, totals, color=colors, alpha=0.8, edgecolor='black')
        ax1.set_ylabel('Всего голов', fontsize=12)
        ax1.set_title('Общее количество голов', fontsize=13, fontweight='bold')
        
        for bar, total in zip(bars1, totals):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{total}', ha='center', va='bottom', fontweight='bold')
        
        # График 2: Голы дома/в гостях
        categories = ['Дома', 'В гостях']
        team1_data = [team1_home, team1_away]
        team2_data = [team2_home, team2_away]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars2_1 = ax2.bar(x - width/2, team1_data, width, label=team1[:12], color='#3498db', alpha=0.8)
        bars2_2 = ax2.bar(x + width/2, team2_data, width, label=team2[:12], color='#e74c3c', alpha=0.8)
        
        ax2.set_ylabel('Голы', fontsize=12)
        ax2.set_title('Голы: дома vs в гостях', fontsize=13, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories)
        ax2.legend()
        
        for bar in bars2_1:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=9)
        
        for bar in bars2_2:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle(f'Сравнение голов: {team1} vs {team2}', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def create_season_goals_plot(self, season_id: str = "all") -> BytesIO:
        if season_id == "all":
            df_filtered = self.df
        else:
            df_filtered = self.df[self.df['SEASON'] == int(season_id)]
        
        home_goals = df_filtered.groupby('HOMETEAM')['HG'].sum()
        away_goals = df_filtered.groupby('AWAYTEAM')['AG'].sum()
        
        total_goals = home_goals.add(away_goals, fill_value=0).astype(int)
        top_teams = total_goals.sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.Reds_r(np.linspace(0.2, 0.7, len(top_teams)))
        
        bars = ax.barh(top_teams.index, top_teams.values, color=colors, alpha=0.8)
        ax.set_xlabel('Забитые голы', fontsize=12)
        ax.set_title('Топ-10 команд по забитым голам', fontsize=14, fontweight='bold', pad=20)
        
        for i, (bar, goals) in enumerate(zip(bars, top_teams.values)):
            ax.text(goals + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{goals}', ha='left', va='center', fontweight='bold')
        
        ax.invert_yaxis()
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf