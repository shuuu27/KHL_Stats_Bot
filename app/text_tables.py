from typing import List, Dict
from data.team_names import TEAM_NAMES

class TextTableFormatter:
    @staticmethod
    def format_season_table(table_data: List[Dict], season_name: str) -> str:
        if not table_data:
            return f"❌ Нет данных для сезона {season_name}"
        
        header = f"🏆 *Турнирная таблица {season_name}*\n\n"
        
        table_header = "№   Команда                И   В   ОТП  П   Ш   +/-  О\n"
        separator = "─" * 55 + "\n"
        
        table_lines = []
        for item in table_data[:15]:  # Показываем топ-15
            team_display = TEAM_NAMES.get(item['team'], item['team'])[:20]
            
            line = f"{item['place']:<3} {team_display:<22} "
            line += f"{item['games']:<3} {item['wins']:<3} "
            line += f"{item['ot_losses']:<4} {item['regular_losses']:<3} "
            line += f"{item['goals_for']}-{item['goals_against']:<4} "
            line += f"{item['goal_diff']:+<4} {item['points']:<3}"
            
            table_lines.append(line)
        
        return header + table_header + separator + "\n".join(table_lines)
    
    @staticmethod
    def format_top_winners(top_data: List[Dict], season_name: str) -> str:
        if not top_data:
            return f"❌ Нет данных для сезона {season_name}"
        
        header = f"🥇 *Топ-{len(top_data)} команд по победам ({season_name})*\n\n"
        
        table_lines = []
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for item in top_data:
            medal = medals[item['place']-1] if item['place'] <= len(medals) else f"{item['place']}."
            team_display = TEAM_NAMES.get(item['team'], item['team'])
            table_lines.append(f"{medal} {team_display} — {item['wins']} побед 🏆")
        
        return header + "\n".join(table_lines)
    
    @staticmethod
    def format_top_points(top_data: List[Dict], season_name: str) -> str:
        if not top_data:
            return f"❌ Нет данных для сезона {season_name}"
        
        header = f"🏆 *Топ-{len(top_data)} команд по очкам ({season_name})*\n\n"
        
        table_lines = []
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for item in top_data:
            medal = medals[item['place']-1] if item['place'] <= len(medals) else f"{item['place']}."
            team_display = TEAM_NAMES.get(item['team'], item['team'])
            table_lines.append(f"{medal} {team_display} — {item['points']} очков 🏅")
        
        return header + "\n".join(table_lines)
    
    @staticmethod
    def format_top_winrate(top_data: List[Dict], season_name: str) -> str:
        if not top_data:
            return f"❌ Нет данных для сезона {season_name}"
        
        header = f"📈 *Топ-{len(top_data)} команд по проценту побед ({season_name})*\n\n"
        
        table_lines = []
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for item in top_data:
            medal = medals[item['place']-1] if item['place'] <= len(medals) else f"{item['place']}."
            team_display = TEAM_NAMES.get(item['team'], item['team'])
            games_info = f"({item['wins']}/{item['total']})"
            table_lines.append(f"{medal} {team_display} — {item['winrate']}% {games_info} 🎯")
        
        return header + "\n".join(table_lines)
    
    @staticmethod
    def format_top_scorers(top_data: List[Dict], season_name: str) -> str:
        if not top_data:
            return f"❌ Нет данных для сезона {season_name}"
        
        header = f"🥅 *Топ-{len(top_data)} команд по забитым голам ({season_name})*\n\n"
        
        table_lines = []
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for item in top_data:
            medal = medals[item['place']-1] if item['place'] <= len(medals) else f"{item['place']}."
            team_display = TEAM_NAMES.get(item['team'], item['team'])
            table_lines.append(f"{medal} {team_display} — {item['goals']} голов 🚨")
        
        return header + "\n".join(table_lines)