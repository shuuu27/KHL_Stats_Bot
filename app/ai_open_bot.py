import pandas as pd
import numpy as np
from app.prediction_engine import PredictionEngine
from app.stats_calculator import StatsCalculator
from app.text_tables import TextTableFormatter
from openai import OpenAI
import os

class KHL_AIBot:
    def __init__(self):
        self.df = pd.read_csv("data/KHL_v1.csv")
        print(f"📊 Загружено {len(self.df)} матчей КХЛ")
        
        self.stats_calc = StatsCalculator(self.df)
        self.prediction_engine = PredictionEngine(self.df)
        self.table_formatter = TextTableFormatter()
        
        self.api_key = os.getenv("VSEGPT_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.vsegpt.ru/v1"
        )
        
        self.gpt_model = "gpt-3.5-turbo"
        
        self.all_teams = sorted(set(self.df['HOMETEAM'].tolist() + self.df['AWAYTEAM'].tolist()))
    
    def extract_teams_from_query(self, query: str) -> list[str]:
        query_lower = query.lower()
        found_teams = []
        
        for team in self.all_teams:
            team_lower = team.lower()
            if team_lower in query_lower:
                found_teams.append(team)
            
            elif any(part in query_lower for part in team_lower.split()):
                if len(team_lower) > 3:
                    found_teams.append(team)
        
        return list(set(found_teams))
    
    def extract_season_from_query(self, query: str):
        
        query_lower = query.lower()
        
        
        for year in range(2008, 2026):
            if str(year) in query_lower:
                next_year = year + 1
                return f"{str(year)[2:]}{str(next_year)[2:]}"
        
        season_keywords = {
            'сейчас': "2526",
            'этом сезоне': "2526",
            'текущем сезоне': "2526",
            'прошлом сезоне': "2425", 
            'позапрошлом сезоне': "2324",
            'сезоне 24/25': "2425",
            'сезоне 23/24': "2324",
            'сезоне 22/23': "2223",
        }
        
        for keyword, season in season_keywords.items():
            if keyword in query_lower:
                return season
        
        return None
    
    def should_show_table_directly(self, query: str) -> bool:
        query_lower = query.lower()
        table_keywords = ['таблица', 'турнирная таблица', 'таблицу', 'распределение','standings', 'ranking']

        if any(keyword in query_lower for keyword in table_keywords):
            return True
        
        top_keywords = ['топ', 'лидеры', 'первые места', 'лучшие команды', 'top', 'leaders']
        if any(keyword in query_lower for keyword in top_keywords):
            return 'не показывай таблицу' not in query_lower
        
        return False
    
    def get_info_for_question(self, query: str) -> dict:
        info = {
            "query": query,
            "teams_found": [],
            "season_found": None,
            "team_stats": {},
            "h2h_stats": {},
            "prediction_data": {},
            "season_stats": {},
            "top_stats": {},
            "show_table_directly": self.should_show_table_directly(query)
        }

        teams = self.extract_teams_from_query(query)
        info["teams_found"] = teams
        
        season = self.extract_season_from_query(query)
        info["season_found"] = season or "all"
        
        for team in teams:
            info["team_stats"][team] = self.stats_calc.get_team_stats(team, season)
            info["team_stats"][f"{team}_home"] = self.stats_calc.get_home_stats(team, season)
            info["team_stats"][f"{team}_away"] = self.stats_calc.get_away_stats(team, season)
            info["team_stats"][f"{team}_form"] = self.stats_calc.get_form_stats(team, 10)
        
        if len(teams) >= 2:
            team1, team2 = teams[0], teams[1]
            info["h2h_stats"] = self.stats_calc.get_head_to_head(team1, team2, season)
            
            try:
                info["prediction_data"] = self.prediction_engine.predict_match(team1, team2)
            except:
                info["prediction_data"] = {}
        
        # Собираем статистику по сезону
        if season or info["show_table_directly"]:
            season_to_use = season or "all"
            info["season_stats"]["table"] = self.stats_calc.get_season_table(season_to_use)
            info["season_stats"]["top_winners"] = self.stats_calc.get_top_winners(season_to_use, 10)
            info["season_stats"]["top_points"] = self.stats_calc.get_top_points(season_to_use, 10)
            info["season_stats"]["top_scorers"] = self.stats_calc.get_top_goal_scorers(season_to_use, 10)
            info["season_stats"]["top_winrate"] = self.stats_calc.get_top_winrate(season_to_use, min_games=10, limit=10)
        
        return info
    
    def generate_table_response(self, info: dict) -> str:

        if not info.get("season_stats", {}).get("table"):
            return "❌ Не удалось получить данные таблицы."
        
        season = info["season_found"] or "all"
        season_name = season if season != "all" else "всех сезонов"
        
        table_data = info["season_stats"]["table"]
        table_text = self.table_formatter.format_season_table(table_data, season_name)
        
        response = table_text + "\n\n"
        
        
        if info["season_stats"].get("top_winners"):
            top_winners = info["season_stats"]["top_winners"][:5]
            response += "🏆 *Лидеры по победам:*\n"
            for item in top_winners:
                response += f"🥇 {item['team']} — {item['wins']} побед\n"
            response += "\n"
        
        if info["season_stats"].get("top_scorers"):
            top_scorers = info["season_stats"]["top_scorers"][:3]
            response += "🥅 *Лучшие по забитым голам:*\n"
            for item in top_scorers:
                response += f"🎯 {item['team']} — {item['goals']} голов\n"
        
        return response
    
    def generate_ai_response(self, query: str, info: dict) -> str:
        
        system_prompt = """Ты - эксперт по статистике Континентальной хоккейной лиги (КХЛ). 
Ты получаешь данные о матчах, статистику команд и прогнозы. 
Используй эту информацию для ответа на вопросы пользователя.

Инструкции:
1. Отвечай на русском языке
2. Будь конкретным и используй предоставленную статистику
3. Делай выводы на основе данных
4. Если данных недостаточно, скажи об этом честно
5. Форматируй ответ так, чтобы он был легко читаем
6. Используй эмодзи для наглядности 🏒🥅🎯📊
7. Включай цифры и проценты
8. Упомяни интересные статистические закономерности

Примеры хороших ответов:
- "Согласно статистике, у команды Ак Барс 65% побед в домашних матчах"
- "За последние 5 встреч ЦСКА выиграл у СКА 3 раза (60%)"
- "Прогноз на матч: победа Ак Барс с вероятностью 58%"
- "СКА лидирует в сезоне с 120 очками, опережая ЦСКА на 15 очков"

Плохие ответы:
- "Не знаю"
- "Посмотрите на сайте"
- "Мне нечего сказать"
- Слишком общие фразы без цифр"""
        
        info_str = self.format_info_for_gpt(info)
        
        user_prompt = f"""Вопрос пользователя: {query}

Статистические данные:
{info_str}

Пожалуйста, дай подробный и информативный ответ на вопрос пользователя, используя предоставленную статистику.
Включай конкретные цифры, проценты и интересные статистические закономерности."""

        try:
            response = self.client.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Ошибка при запросе к GPT: {e}")
            return 
    
    def format_info_for_gpt(self, info: dict) -> str:

        formatted = []
        
        formatted.append(f"Запрос пользователя: {info['query']}")
        
        
        if info["teams_found"]:
            formatted.append(f"\nНайдены команды: {', '.join(info['teams_found'])}")
        
        if info["season_found"] and info["season_found"] != "all":
            formatted.append(f"Сезон: {info['season_found']}")
        
        # Статистика команд
        for team, stats in info["team_stats"].items():
            if stats and isinstance(stats, dict) and team in info["teams_found"]:
                formatted.append(f"\nСтатистика команды {team}:")
                if 'games' in stats:
                    formatted.append(f"  Матчей: {stats.get('games', 'нет данных')}")
                    formatted.append(f"  Побед: {stats.get('wins', 'нет данных')} ({stats.get('win_rate', 'нет данных')})")
                    formatted.append(f"  Голы: забито {stats.get('goals_scored', 'нет данных')}, пропущено {stats.get('goals_conceded', 'нет данных')}")
                    formatted.append(f"  Разница голов: {stats.get('goal_difference', 'нет данных')}")
                    formatted.append(f"  Очки: {stats.get('points', 'нет данных')}")
        
        # H2H статистика
        if info["h2h_stats"]:
            h2h = info["h2h_stats"]
            formatted.append(f"\nВстречи {h2h.get('team1', '')} vs {h2h.get('team2', '')}:")
            formatted.append(f"  Всего матчей: {h2h.get('total_games', 0)}")
            formatted.append(f"  Побед {h2h.get('team1', '')}: {h2h.get('team1_wins', 0)} ({h2h.get('team1_winrate', 'нет данных')})")
            formatted.append(f"  Побед {h2h.get('team2', '')}: {h2h.get('team2_wins', 0)} ({h2h.get('team2_winrate', 'нет данных')})")
        
        # Прогноз
        if info["prediction_data"] and "prediction" in info["prediction_data"]:
            pred = info["prediction_data"]["prediction"]
            probs = info["prediction_data"].get("probabilities", {})
            
            formatted.append("\nПрогноз на матч:")
            formatted.append(f"  {pred.get('description', 'нет данных')}")
            if probs:
                formatted.append(f"  Вероятности: победа хозяев {probs.get('home_win', 0):.1%}, победа гостей {probs.get('away_win', 0):.1%}")
        
        # Информация о сезоне (для GPT, но не полная таблица)
        if info["season_stats"].get("table"):
            table = info["season_stats"]["table"]
            formatted.append(f"\nИнформация о сезоне {info['season_found']}:")
            formatted.append(f"  Всего команд: {len(table)}")
            if table:
                formatted.append(f"  Лидер: {table[0]['team']} с {table[0]['points']} очками")
                if len(table) > 1:
                    formatted.append(f"  Второе место: {table[1]['team']} с {table[1]['points']} очками")
        
        return "\n".join(formatted)
    
    def format_team_stats_fallback(self, team: str, info: dict) -> str:
        stats = info["team_stats"].get(team, {})
        if not stats:
            return f"Нет данных о команде {team}"
        
        home_stats = info["team_stats"].get(f"{team}_home", {})
        away_stats = info["team_stats"].get(f"{team}_away", {})
        form_stats = info["team_stats"].get(f"{team}_form", {})
        
        response = f"""
📊 *Статистика команды {team}*:

🎯 Общая статистика:
   • Матчей: {stats.get('games', 0)}
   • Побед: {stats.get('wins', 0)} ({stats.get('win_rate', '0%')})
   • Голы: {stats.get('goals_scored', 0)}-{stats.get('goals_conceded', 0)} (разница: {stats.get('goal_difference', 0)})
   • Очки: {stats.get('points', 0)}

🏠 Домашняя статистика:
   • Матчей: {home_stats.get('games', 0)}
   • Побед: {home_stats.get('wins', 0)} ({home_stats.get('win_rate', '0%')})
   • Голы: {home_stats.get('goals_scored', 0)}-{home_stats.get('goals_conceded', 0)}

🚌 Гостевая статистика:
   • Матчей: {away_stats.get('games', 0)}
   • Побед: {away_stats.get('wins', 0)} ({away_stats.get('win_rate', '0%')})
   • Голы: {away_stats.get('goals_scored', 0)}-{away_stats.get('goals_conceded', 0)}
"""
        
        if form_stats.get('last_games'):
            response += "\n📈 Последние матчи:\n"
            for game in form_stats['last_games'][:5]:
                result = "✅" if game['winner'] == team else "❌"
                response += f"   {result} {game['home_team']} {game['score']} {game['away_team']}\n"
        
        return response
    
    def format_prediction_fallback(self, team1: str, team2: str, info: dict) -> str:
        """Форматирование прогноза (fallback)"""
        prediction = info.get("prediction_data", {})
        h2h = info.get("h2h_stats", {})
        
        if "error" in prediction:
            pred_text = "Не могу сделать точный прогноз"
        else:
            pred_info = prediction.get("prediction", {})
            probs = prediction.get("probabilities", {})
            pred_text = f"{pred_info.get('description', 'Нет прогноза')}\n\n"
            if probs:
                pred_text += f"Вероятности:\n"
                pred_text += f"• {team1}: {probs.get('home_win', 0):.1%}\n"
                pred_text += f"• {team2}: {probs.get('away_win', 0):.1%}\n"
                pred_text += f"• Ничья: {probs.get('draw', 0):.1%}"
        
        response = f"""
🏒 *Прогноз на матч {team1} - {team2}*:

🎯 {pred_text}
"""
        
        if h2h:
            response += f"""
📊 Исторические встречи:
   • Всего матчей: {h2h.get('total_games', 0)}
   • Побед {team1}: {h2h.get('team1_wins', 0)} ({h2h.get('team1_winrate', '0%')})
   • Побед {team2}: {h2h.get('team2_wins', 0)} ({h2h.get('team2_winrate', '0%')})
"""
        
        return response
    
    def ask(self, query: str) -> str:

        print(f"\n🧐 Вопрос: {query}")
        
        info = self.get_info_for_question(query)
        
        
        if info.get("show_table_directly"):
            print("📋 Показываем таблицу напрямую")
            return self.generate_table_response(info)
        
        print(f"📊 Собрано данных: {len(info['teams_found'])} команд, сезон: {info['season_found']}")
        
        # Генерируем ответ
        response = self.generate_ai_response(query, info)
        
        return response


# Пример использования
if __name__ == "__main__":

    bot = KHL_AIBot()
    
    print("=" * 60)
    print("🤖 KHL AI Bot - Тестирование")
    print("=" * 60)


    print("\n💬 Интерактивный режим (для выхода введите 'q' или 'exit')")
    while True:
        user_input = input("\nВы: ")
        if user_input.lower() in ['q', 'exit', 'quit']:
            print("До свидания! 👋")
            break
        
        answer = bot.ask(user_input)
        print(f"\nБот: {answer}")