from typing import Dict
from data.team_names import TEAM_NAMES


class StatsFormatter:
    @staticmethod
    def format_team_stats(stats: Dict, season_name: str) -> str:
        if not stats:
            return "❌ Нет данных для этой команды в выбранном сезоне."
        
        team_display = TEAM_NAMES.get(stats['team'], stats['team'])
        
        return (
            f"🏒 *{team_display}*\n"
            f"📅 Сезон: *{season_name}*\n\n"
            
            f"📊 *Основная статистика:*\n"
            f"• Игр: {stats['games']}\n"
            f"• Побед: {stats['wins']}\n"
            f"• Поражений: {stats['losses']}\n"
            f"• Win Rate: {stats['win_rate']}\n\n"
            
            f"🥅 *Голы:*\n"
            f"• Забито: {stats['goals_scored']}\n"
            f"• Пропущено: {stats['goals_conceded']}\n"
            f"• Разница: {stats['goal_difference']} "
            f"({stats['avg_goals_per_game']}-{stats['avg_conceded_per_game']} за игру)\n\n"
            
            f"🏆 *Очки:* {stats['points']}"
        )
    
    @staticmethod
    def format_head_to_head(h2h_stats: Dict, season_name: str) -> str:
        if not h2h_stats:
            return "❌ Эти команды не играли друг с другом в выбранном сезоне."
        
        team1_display = TEAM_NAMES.get(h2h_stats['team1'], h2h_stats['team1'])
        team2_display = TEAM_NAMES.get(h2h_stats['team2'], h2h_stats['team2'])
        
        return (
            f"⚔️ *Head-to-Head*\n"
            f"{team1_display} vs {team2_display}\n"
            f"📅 Сезон: *{season_name}*\n\n"
            
            f"🔴 *{team1_display}*\n"
            f"• Побед: {h2h_stats['team1_wins']}\n"
            f"• Win Rate: {h2h_stats['team1_winrate']}\n\n"
            
            f"🔵 *{team2_display}*\n"
            f"• Побед: {h2h_stats['team2_wins']}\n"
            f"• Win Rate: {h2h_stats['team2_winrate']}\n\n"
            
            f"📊 Всего игр: *{h2h_stats['total_games']}*\n"
            f"⚖️ Баланс: {h2h_stats['team1_wins']}-{h2h_stats['team2_wins']}"
        )