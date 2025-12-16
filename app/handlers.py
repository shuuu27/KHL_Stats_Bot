from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.prediction_engine import PredictionEngine
from app.prediction_formatter import PredictionFormatter



from app.stats_calculator import StatsCalculator
from app.formatters import StatsFormatter
from app.text_tables import TextTableFormatter
from app.plot_generator import PlotGenerator
from app.data_loader import loader
from data.team_names import TEAM_NAMES
from app.keyboards import (
    get_main_menu, get_back_button, 
    get_teams_keyboard, get_seasons_keyboard,
    get_stats_options_keyboard, get_yes_no_keyboard,
    get_back_only_keyboard, get_tops_menu_keyboard,
    get_plot_options_keyboard, get_plot_seasons_keyboard,
    get_prediction_keyboard, get_prediction_teams_keyboard
)

prediction_engine = None
calculator = None
plot_generator = None
router = Router()

class StatsStates(StatesGroup):
    choosing_team = State()
    choosing_season = State()
    choosing_option = State()
    choosing_h2h_team = State()
    choosing_plot_type = State()
    prediction_team1 = State()
    prediction_team2 = State() 

@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = """
🏒 *Добро пожаловать в KHL Stats Bot!*

Я помогу вам получить статистику команд Континентальной Хоккейной Лиги:

📊 *Статистика команды* — подробная статистика любой команды
🔮 *Предсказание матча* — ML прогноз исхода матча
🏆 *Таблица сезона* — турнирная таблица любого сезона
📈 *Топы и рекорды* — лучшие показатели и достижения

Выберите действие в меню ниже!
    """    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📚 *Помощь по KHL Stats Bot*

*Основные функции:*
📊 **Статистика команды** — выберите команду и сезон
📈 **Топы и рекорды** — различные рейтинги команд
🔮 **Предсказание матча** — выберите две команды
🏆 **Таблица сезона** — турнирная таблица выбранного сезона


*Как пользоваться:*
1. Используйте кнопки меню для навигации
2. Выбирайте команды и сезоны из списка
3. Просматривайте статистику в удобном формате

*Данные:*
• Сезоны с 2008/09 по 2019/20
• Все команды КХЛ за этот период
• Регулярный чемпионат + плей-офф
    """
    
    await message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "📋 Главное меню:",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "📊 Статистика команды")
async def stats_start(message: Message, state: FSMContext):
    await message.answer(
        "Выберите команду для просмотра статистики:",
        reply_markup=get_teams_keyboard()
    )
    await state.set_state(StatsStates.choosing_team)

@router.message(F.text == "📈 Графики и визуализация")
async def plots_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📊 *Графики и визуализация*\n\nВыберите тип графика:",
        parse_mode="Markdown",
        reply_markup=get_plot_options_keyboard()
    )

@router.message(F.text == "🏆 Таблица сезона")
async def season_table_start(message: Message):
    await message.answer(
        "📅 *Таблица сезона*\n\nВыберите сезон для просмотра турнирной таблицы:",
        parse_mode="Markdown",
        reply_markup=get_seasons_keyboard("table_")
    )

@router.message(F.text == "📈 Топы и рекорды")
async def tops_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏆 *Топы и рекорды*\n\nВыберите сезон для анализа:",
        parse_mode="Markdown",
        reply_markup=get_seasons_keyboard("top_menu_")
    )

@router.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    await cmd_help(message)

@router.message(F.text == "⬅️ Назад в меню")
async def back_to_menu(message: Message):
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data.startswith("team_"))
async def team_selected(callback: CallbackQuery, state: FSMContext):
    try:
        team_id = callback.data.replace("team_", "")
        
        if not loader.teams or team_id not in loader.teams:
            await callback.answer(
                f"❌ Команда '{team_id}' не найдена в базе данных",
                show_alert=True
            )
            await callback.message.edit_text(
                "❌ Команда не найдена. Пожалуйста, выберите команду из списка:",
                reply_markup=get_teams_keyboard()
            )
            return
        
        team_display_name = TEAM_NAMES.get(team_id, f"{team_id} 🏒")
        await state.update_data(selected_team=team_id)
        
        message_text = f"✅ *Выбрана команда:* {team_display_name}\n\n🏆 *Теперь выберите сезон:*"
        
        await callback.message.edit_text(
            message_text,
            parse_mode="Markdown",
            reply_markup=get_seasons_keyboard("stats_season_")
        )
        await state.set_state(StatsStates.choosing_season)
              
    except Exception:
        error_message = "😕 *Произошла непредвиденная ошибка*\n\nПожалуйста, попробуйте:\n1. Выбрать команду заново\n2. Если ошибка повторяется, напишите /menu\n3. Или попробуйте позже"
        
        try:
            await callback.message.edit_text(
                error_message,
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
        except:
            await callback.message.answer(
                error_message,
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
        await state.clear()
        
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("stats_season_"))
async def season_selected(callback: CallbackQuery, state: FSMContext):
    try:
        season_id = callback.data.replace("stats_season_", "")
        await state.update_data(selected_season=season_id)
        data = await state.get_data()
        team_id = data.get('selected_team')

        if not team_id:
            await callback.message.edit_text(
                "❌ Что-то пошло не так. Выберите команду заново.",
                reply_markup=get_teams_keyboard()
            )
            await state.set_state(StatsStates.choosing_team)
            return
        
        if season_id == "all":
            season_name = "Все сезоны"
        elif len(season_id) == 3:
            season_name = f"200{season_id[0]}/20{season_id[1:]}"
        else:
            season_name = f"20{season_id[:2]}/{season_id[2:]}"
        
        team_display_name = TEAM_NAMES.get(team_id, team_id)
        
        await callback.message.edit_text(
            f"📊 *Статистика команды*\n\n• Команда: *{team_display_name}*\n• Сезон: *{season_name}*\n\nВыберите тип статистики:",
            parse_mode="Markdown",
            reply_markup=get_stats_options_keyboard()
        )
        await state.set_state(StatsStates.choosing_option)
        
    except:
        await callback.answer("❌ Произошла ошибка. Попробуйте еще раз.", show_alert=True)
    finally:
        await callback.answer()

@router.callback_query(F.data == "stats_general")
async def show_general_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    season_id = data.get('selected_season')
    
    stats = calculator.get_team_stats(team_id, season_id)
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    response = StatsFormatter.format_team_stats(stats, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_yes_no_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "stats_h2h")
async def show_h2h_stats(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите вторую команду для сравнения:",
        reply_markup=get_teams_keyboard("h2h_second_")
    )
    await state.set_state(StatsStates.choosing_h2h_team)
    await callback.answer()

@router.callback_query(F.data.startswith("h2h_second_"))
async def process_h2h_selection(callback: CallbackQuery, state: FSMContext):
    try:
        team2_id = callback.data.replace("h2h_second_", "")
        data = await state.get_data()
        team1_id = data.get('selected_team')
        season_id = data.get('selected_season')
        
        if team1_id == team2_id:
            await callback.answer("❌ Выберите другую команду для сравнения!", show_alert=True)
            return
        
        h2h_stats = calculator.get_head_to_head(team1_id, team2_id, season_id)
        
        if season_id == "all":
            season_name = "Все сезоны"
        elif len(season_id) == 3:
            season_name = f"200{season_id[0]}/20{season_id[1:]}"
        else:
            season_name = f"20{season_id[:2]}/{season_id[2:]}"
        
        response = StatsFormatter.format_head_to_head(h2h_stats, season_name)
        
        await callback.message.edit_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_yes_no_keyboard()
        )
        await state.set_state(StatsStates.choosing_option)
        
    except:
        await callback.answer("❌ Произошла ошибка. Попробуйте еще раз.", show_alert=True)
    finally:
        await callback.answer()

@router.callback_query(F.data == "stats_home")
async def show_home_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    season_id = data.get('selected_season')
    
    stats = calculator.get_home_stats(team_id, season_id)
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    if not stats:
        response = f"❌ Нет данных о домашних играх команды *{TEAM_NAMES.get(team_id, team_id)}* в сезоне {season_name}"
    else:
        team_display = TEAM_NAMES.get(stats['team'], stats['team'])
        response = (
            f"🏠 *Домашняя статистика {team_display}*\n"
            f"📅 Сезон: *{season_name}*\n\n"
            f"📊 *Статистика дома:*\n"
            f"• Игр дома: {stats['games']}\n"
            f"• Побед дома: {stats['wins']}\n"
            f"• Поражений дома: {stats['losses']}\n"
            f"• Win Rate дома: {stats['win_rate']}\n\n"
            f"🥅 *Голы дома:*\n"
            f"• Забито: {stats['goals_scored']}\n"
            f"• Пропущено: {stats['goals_conceded']}\n"
            f"• Разница: {stats['goal_difference']}\n\n"
            f"🏆 *Очки дома:* {stats['points']}"
        )
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_yes_no_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "stats_away")
async def show_away_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    season_id = data.get('selected_season')
    
    stats = calculator.get_away_stats(team_id, season_id)
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    if not stats:
        response = f"❌ Нет данных о гостевых играх команды *{TEAM_NAMES.get(team_id, team_id)}* в сезоне {season_name}"
    else:
        team_display = TEAM_NAMES.get(stats['team'], stats['team'])
        response = (
            f"✈️ *Гостевая статистика {team_display}*\n"
            f"📅 Сезон: *{season_name}*\n\n"
            f"📊 *Статистика в гостях:*\n"
            f"• Игр в гостях: {stats['games']}\n"
            f"• Побед в гостях: {stats['wins']}\n"
            f"• Поражений в гостях: {stats['losses']}\n"
            f"• Win Rate в гостях: {stats['win_rate']}\n\n"
            f"🥅 *Голы в гостях:*\n"
            f"• Забито: {stats['goals_scored']}\n"
            f"• Пропущено: {stats['goals_conceded']}\n"
            f"• Разница: {stats['goal_difference']}\n\n"
            f"🏆 *Очки в гостях:* {stats['points']}"
        )
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_yes_no_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "stats_form")
async def show_form_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    
    form_stats = calculator.get_form_stats(team_id, n_games=10)
    
    if not form_stats:
        response = f"❌ Нет данных о последних играх команды *{TEAM_NAMES.get(team_id, team_id)}*"
    else:
        team_display = TEAM_NAMES.get(form_stats['team'], form_stats['team'])
        response = f"📈 *Форма команды {team_display}*\n\n"
        response += f"Последние {form_stats['games']} игр:\n"
        response += f"• Побед: {form_stats['wins']}\n"
        response += f"• Поражений: {form_stats['losses']}\n"
        response += f"• Win Rate: {form_stats['win_rate']}\n\n"
        
        if form_stats['last_games']:
            response += "📋 *Последние игры:*\n"
            for game in form_stats['last_games'][:5]:
                result = "✅" if game['winner'] == team_id else "❌"
                venue = "🏠" if game['is_home'] else "✈️"
                opponent = game['away_team'] if game['is_home'] else game['home_team']
                opponent_display = TEAM_NAMES.get(opponent, opponent)
                response += f"{result} {venue} {game['score']} vs {opponent_display}\n"
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_yes_no_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "stats_goals")
async def show_goals_stats(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    season_id = data.get('selected_season')
    
    stats = calculator.get_team_stats(team_id, season_id)
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    if not stats:
        response = f"❌ Нет данных по голам команды *{TEAM_NAMES.get(team_id, team_id)}* в сезоне {season_name}"
    else:
        team_display = TEAM_NAMES.get(stats['team'], stats['team'])
        response = (
            f"🥅 *Статистика голов {team_display}*\n"
            f"📅 Сезон: *{season_name}*\n\n"
            f"📊 *Голы за сезон:*\n"
            f"• Забито: {stats['goals_scored']}\n"
            f"• Пропущено: {stats['goals_conceded']}\n"
            f"• Разница: {stats['goal_difference']}\n\n"
            f"📈 *Средние показатели за игру:*\n"
            f"• Забивает: {stats['avg_goals_per_game']}\n"
            f"• Пропускает: {stats['avg_conceded_per_game']}\n\n"
            f"⚖️ *Баланс:* {stats['avg_goals_per_game']}-{stats['avg_conceded_per_game']}"
        )
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_yes_no_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "yes")
async def handle_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_id = data.get('selected_team')
    
    await callback.message.edit_text(
        f"Выберите тип статистики для команды *{team_id}*:",
        parse_mode="Markdown",
        reply_markup=get_stats_options_keyboard()
    )
    await state.set_state(StatsStates.choosing_option)
    await callback.answer()

@router.callback_query(F.data == "no")
async def handle_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Возвращаемся в главное меню:\n\nВыберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("table_"))
async def show_season_table(callback: CallbackQuery):
    season_id = callback.data.replace("table_", "")
    
    if season_id == "all":
        await callback.message.edit_text(
            "❌ Для отображения турнирной таблицы нужно выбрать конкретный сезон.\nВыберите сезон из списка:",
            reply_markup=get_seasons_keyboard("table_")
        )
    else:
            
        if len(season_id) == 3:
            season_name = f"200{season_id[0]}/20{season_id[1:]}"
        else:
            season_name = f"20{season_id[:2]}/{season_id[2:]}"
        
        table_data = calculator.get_season_table(season_id)
        response = TextTableFormatter.format_season_table(table_data, season_name)
        
        await callback.message.edit_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_back_only_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("top_menu_"))
async def top_menu_selected(callback: CallbackQuery, state: FSMContext):
    season_id = callback.data.replace("top_menu_", "")
    await state.update_data(selected_season=season_id)
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    await callback.message.edit_text(
        f"🏆 *Топы и рекорды*\n📅 Сезон: *{season_name}*\n\nВыберите тип топа:",
        parse_mode="Markdown",
        reply_markup=get_tops_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "top_winners")
async def show_top_winners(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    season_id = data.get('selected_season', 'all')
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    top_data = calculator.get_top_winners(season_id, limit=10)
    response = TextTableFormatter.format_top_winners(top_data, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "top_points")
async def show_top_points(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    season_id = data.get('selected_season', 'all')
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    top_data = calculator.get_top_points(season_id, limit=10)
    response = TextTableFormatter.format_top_points(top_data, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "top_winrate")
async def show_top_winrate(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    season_id = data.get('selected_season', 'all')
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    top_data = calculator.get_top_winrate(season_id, limit=10)
    response = TextTableFormatter.format_top_winrate(top_data, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "top_scorers")
async def show_top_scorers(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    season_id = data.get('selected_season', 'all')
    
    if season_id == "all":
        season_name = "Все сезоны"
    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    
    top_data = calculator.get_top_goal_scorers(season_id, limit=10)
    response = TextTableFormatter.format_top_scorers(top_data, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "top_full_table")
async def show_full_table(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    season_id = data.get('selected_season', 'all')
    
    if season_id == "all":
        await callback.answer("❌ Выберите конкретный сезон для просмотра таблицы", show_alert=True)
        return

    elif len(season_id) == 3:
        season_name = f"200{season_id[0]}/20{season_id[1:]}"
    else:
        season_name = f"20{season_id[:2]}/{season_id[2:]}"
    table_data = calculator.get_season_table(season_id)
    response = TextTableFormatter.format_season_table(table_data, season_name)
    
    await callback.message.edit_text(
        response,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("top_"))
async def show_tops(callback: CallbackQuery):
    season_id = callback.data.replace("top_", "")
    
    if season_id == "all":
        season_text = "за все сезоны"
    elif len(season_id) == 3:
        season_text = f"в сезоне 200{season_id[0]}/20{season_id[1:]}"
    else:
        season_text = f"в сезоне 20{season_id[:2]}/20{season_id[2:]}"
    
    await callback.message.edit_text(
        f"📈 *Топы и рекорды {season_text}*\n\nВыберите тип топа:",
        parse_mode="Markdown",
        reply_markup=get_tops_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main_menu")
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    

    await callback.message.edit_text(
        "📋 *Главное меню:*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

    await callback.answer()

@router.callback_query(F.data == "plot_winners")
async def plot_winners_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(plot_type="winners")
    await callback.message.edit_text(
        "📊 *Топ победителей*\n\nВыберите сезон для графика:",
        parse_mode="Markdown",
        reply_markup=get_plot_seasons_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "plot_points")
async def plot_points_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(plot_type="points")
    await callback.message.edit_text(
        "🏆 *Топ по очкам*\n\nВыберите сезон для графика:",
        parse_mode="Markdown",
        reply_markup=get_plot_seasons_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "plot_goals")
async def plot_goals_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(plot_type="goals")
    await callback.message.edit_text(
        "🥅 *Топ по голам*\n\nВыберите сезон для графика:",
        parse_mode="Markdown",
        reply_markup=get_plot_seasons_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "plot_form")
async def plot_form_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📈 *Форма команды*\n\nВыберите команду для графика:",
        parse_mode="Markdown",
        reply_markup=get_teams_keyboard("plot_team_")
    )
    await callback.answer()

@router.callback_query(F.data == "plot_goals_compare")
async def plot_goals_compare_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚔️ *Сравнение голов*\n\nВыберите первую команду:",
        parse_mode="Markdown",
        reply_markup=get_teams_keyboard("plot_compare1_")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("plot_season_"))
async def plot_season_selected(callback: CallbackQuery, state: FSMContext):
    try:
        season_id = callback.data.replace("plot_season_", "")
        data = await state.get_data()
        plot_type = data.get('plot_type', 'winners')
        
        await callback.message.edit_text(
            "🔄 Генерирую график...",
            parse_mode="Markdown"
        )
        
        if plot_type == "winners":
            plot_buffer = plot_generator.create_top_winners_plot(season_id)
            caption = f"📊 Топ-10 команд по победам"
        elif plot_type == "points":
            plot_buffer = plot_generator.create_top_points_plot(season_id)
            caption = f"🏆 Топ-10 команд по очкам"
        elif plot_type == "goals":
            plot_buffer = plot_generator.create_season_goals_plot(season_id)
            caption = f"🥅 Топ-10 команд по голам"
        else:
            await callback.answer("❌ Неизвестный тип графика", show_alert=True)
            return
        
        if season_id == "all":
            season_name = "Все сезоны"
        elif len(season_id) == 3:
            season_name = f"200{season_id[0]}/20{season_id[1:]}"
        else:
            season_name = f"20{season_id[:2]}/{season_id[2:]}"
        
        caption += f"\n📅 Сезон: {season_name}"
        
        photo = BufferedInputFile(plot_buffer.read(), filename="plot.png")
        
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_back_only_keyboard()
        )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("plot_team_"))
async def plot_team_selected(callback: CallbackQuery, state: FSMContext):
    try:
        team_id = callback.data.replace("plot_team_", "")
        
        await callback.message.edit_text(
            f"🔄 Генерирую график формы для команды {team_id}...",
            parse_mode="Markdown"
        )
        
        plot_buffer = plot_generator.create_team_form_plot(team_id, n_games=10)
        
        if plot_buffer:
            caption = f"📈 Форма команды {team_id}\nПоследние 10 игр"
            
            photo = BufferedInputFile(plot_buffer.read(), filename="form_plot.png")
            
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=get_back_only_keyboard()
            )
        else:
            await callback.message.edit_text(
                f"❌ Нет данных для команды {team_id}",
                parse_mode="Markdown",
                reply_markup=get_back_only_keyboard()
            )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    finally:
        await callback.answer()

@router.callback_query(F.data.startswith("plot_compare1_"))
async def plot_compare1_selected(callback: CallbackQuery, state: FSMContext):
    team1_id = callback.data.replace("plot_compare1_", "")
    await state.update_data(plot_team1=team1_id)
    
    await callback.message.edit_text(
        f"Первая команда: {team1_id}\n\nВыберите вторую команду:",
        parse_mode="Markdown",
        reply_markup=get_teams_keyboard("plot_compare2_")
    )
    await callback.answer()

@router.callback_query(F.data.startswith("plot_compare2_"))
async def plot_compare2_selected(callback: CallbackQuery, state: FSMContext):
    try:
        team2_id = callback.data.replace("plot_compare2_", "")
        data = await state.get_data()
        team1_id = data.get('plot_team1')
        season_id = data.get('selected_season', 'all')
        
        if team1_id == team2_id:
            await callback.answer("❌ Выберите другую команду!", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"🔄 Сравниваю голы: {team1_id} vs {team2_id}...",
            parse_mode="Markdown"
        )
        
        plot_buffer = plot_generator.create_goals_comparison_plot(team1_id, team2_id, season_id)
        
        if season_id == "all":
            season_name = "Все сезоны"
        elif len(season_id) == 3:
            season_name = f"200{season_id[0]}/20{season_id[1:]}"
        else:
            season_name = f"20{season_id[:2]}/{season_id[2:]}"
        
        caption = f"⚔️ Сравнение голов\n{team1_id} vs {team2_id}\n📅 Сезон: {season_name}"
        
        photo = BufferedInputFile(plot_buffer.read(), filename="comparison_plot.png")
        
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_back_only_keyboard()
        )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    finally:
        await callback.answer()


@router.message(F.text == "🔮 Предсказание матча")
async def prediction_start(message: Message):
    await message.answer(
        "🔮 *Система предсказаний матчей*\n\n"
        "Используйте машинное обучение для прогноза исхода матча!\n"
        "Модель анализирует исторические данные и статистику команд.",
        parse_mode="Markdown",
        reply_markup=get_prediction_keyboard()
    )

# Обработчики для предсказаний
@router.callback_query(F.data == "make_prediction")
async def make_prediction_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🏠 *Выберите домашнюю команду:*",
        parse_mode="Markdown",
        reply_markup=get_prediction_teams_keyboard(step=1)
    )
    await state.set_state(StatsStates.prediction_team1)
    await callback.answer()

@router.callback_query(F.data.startswith("pred_team1_"))
async def prediction_team1_selected(callback: CallbackQuery, state: FSMContext):
    team1_id = callback.data.replace("pred_team1_", "")
    await state.update_data(prediction_team1=team1_id)
    
    team_display = TEAM_NAMES.get(team1_id, team1_id)
    
    await callback.message.edit_text(
        f"🏠 Домашняя команда: *{team_display}*\n\n"
        "✈️ *Выберите гостевую команду:*",
        parse_mode="Markdown",
        reply_markup=get_prediction_teams_keyboard(step=2)
    )
    await state.set_state(StatsStates.prediction_team2)
    await callback.answer()

@router.callback_query(F.data.startswith("pred_team2_"))
async def prediction_team2_selected(callback: CallbackQuery, state: FSMContext):
    try:
        team2_id = callback.data.replace("pred_team2_", "")
        data = await state.get_data()
        team1_id = data.get('prediction_team1')
        
        if team1_id == team2_id:
            await callback.answer("❌ Выберите другую команду!", show_alert=True)
            return
        
        await callback.message.edit_text(
            "🧠 *Анализирую данные и делаю предсказание...*",
            parse_mode="Markdown"
        )
        
        prediction = prediction_engine.predict_match(team1_id, team2_id)

        h2h_stats = prediction_engine.get_head_to_head_stats(team1_id, team2_id)

        prediction_text = PredictionFormatter.format_prediction(prediction)
        h2h_text = PredictionFormatter.format_head_to_head(h2h_stats, team1_id, team2_id)
        

        full_response = prediction_text + "\n\n" + h2h_text
        
        await callback.message.edit_text(
            full_response,
            parse_mode="Markdown",
            reply_markup=get_back_only_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
    finally:
        await callback.answer()

@router.callback_query(F.data == "show_h2h_stats")
async def show_h2h_stats_prediction(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🏠 *Выберите первую команду для истории встреч:*",
        parse_mode="Markdown",
        reply_markup=get_prediction_teams_keyboard(step=1)
    )
    await state.set_state(StatsStates.prediction_team1)
    await callback.answer()

@router.callback_query(F.data == "model_accuracy")
async def show_model_accuracy(callback: CallbackQuery):
    accuracy_info = """
📊 *Информация о модели*

*Метод:* Random Forest Classifier
*Деревьев:* 100
*Признаки:*
• Кодированные названия команд
• Домашний winrate команд
• Гостевой winrate команд
• Общий winrate команд

*Данные для обучения:*
• Все матчи КХЛ (2008-2020)
• Балансировка классов

*Точность модели:* ~65-70% (на тестовой выборке)
"""
    
    await callback.message.edit_text(
        accuracy_info,
        parse_mode="Markdown",
        reply_markup=get_back_only_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_predictions")
async def back_to_predictions(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🔮 *Система предсказаний матчей*\n\n"
        "Выберите действие:",
        parse_mode="Markdown",
        reply_markup=get_prediction_keyboard()
    )
    await callback.answer()