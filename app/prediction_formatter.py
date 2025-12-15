from typing import Dict
from data.team_names import TEAM_NAMES

class PredictionFormatter:
    @staticmethod
    def format_prediction(prediction_data: Dict) -> str:
        if "error" in prediction_data:
            return f"❌ {prediction_data['error']}"
        
        home_team = prediction_data['home_team']
        away_team = prediction_data['away_team']
        
        home_display = TEAM_NAMES.get(home_team, home_team)
        away_display = TEAM_NAMES.get(away_team, away_team)

        result = prediction_data['prediction']
        probabilities = prediction_data['probabilities']
  
        home_prob = probabilities.get('home_win', 0) * 100
        away_prob = probabilities.get('away_win', 0) * 100
        draw_prob = probabilities.get('draw', 0) * 100
        

        home_stats = prediction_data['team_stats']['home']
        away_stats = prediction_data['team_stats']['away']
        
        response = f"🔮 *Предсказание матча*\n\n"
        response += f"🏠 *{home_display}* vs ✈️ *{away_display}*\n\n"
        
        response += f"🎯 *Прогноз:* {result['description']}\n\n"
        
        response += f"📊 *Вероятности:*\n"
        response += f"• {home_display}: {home_prob:.1f}%\n"
        response += f"• {away_display}: {away_prob:.1f}%\n"
        
        response += f"📈 *Статистика команд:*\n"
        response += f"🏠 {home_display}:\n"
        response += f"  • Домашний winrate: {home_stats['home_win_rate']*100:.1f}%\n"
        response += f"  • Общий winrate: {home_stats['overall_win_rate']*100:.1f}%\n"
        response += f"  • Всего игр: {home_stats['total_games']}\n\n"
        
        response += f"✈️ {away_display}:\n"
        response += f"  • Гостевой winrate: {away_stats['away_win_rate']*100:.1f}%\n"
        response += f"  • Общий winrate: {away_stats['overall_win_rate']*100:.1f}%\n"
        response += f"  • Всего игр: {away_stats['total_games']}\n"
        
        return response
    
    @staticmethod
    def format_head_to_head(h2h_data: Dict, team1: str, team2: str) -> str:
        if h2h_data['total_games'] == 0:
            return f"❌ Команды {team1} и {team2} не играли друг с другом.\n"
        
        team1_display = TEAM_NAMES.get(team1, team1)
        team2_display = TEAM_NAMES.get(team2, team2)
        
        response = f"⚔️ *История личных встреч*\n\n"
        response += f"{team1_display} vs {team2_display}\n\n"
        
        response += f"📊 *Всего игр:* {h2h_data['total_games']}\n"
        response += f"• {team1_display}: {h2h_data[f'{team1}_wins']} побед ({h2h_data[f'{team1}_winrate']*100:.1f}%)\n"
        response += f"• {team2_display}: {h2h_data[f'{team2}_wins']} побед ({h2h_data[f'{team2}_winrate']*100:.1f}%)\n\n"
        
        if 'last_games' in h2h_data and h2h_data['last_games']:
            response += f"📋 *Последние встречи:*\n"
            for game in h2h_data['last_games']:
                winner = TEAM_NAMES.get(game['WINNER'], game['WINNER'])
                response += f"• {game['HOMETEAM']} {game['SCORE']} {game['AWAYTEAM']} (Победитель: {winner})\n"
        
        return response
    
    @staticmethod
    def format_confidence_level(probability: float) -> str:

        if probability >= 70:
            return "🎯 Высокая уверенность"
        elif probability >= 50:
            return "⚠️ Средняя уверенность"
        else:
            return "🤔 Низкая уверенность"