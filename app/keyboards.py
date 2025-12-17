from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.data_loader import loader
from data.team_names import TEAM_NAMES


def get_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📊 Статистика команды"),
        KeyboardButton(text="🔮 Предсказание матча")
    )
    
    builder.row(
        KeyboardButton(text="🏆 Таблица сезона"),
        KeyboardButton(text="📈 Топы и рекорды")
    )
    
    builder.row(
        KeyboardButton(text="ℹ️ Помощь")
    )
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберите действие...")

def get_back_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Назад в меню"))
    return builder.as_markup(resize_keyboard=True)



def get_teams_keyboard(action_prefix: str = "team_") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if loader.teams:
        for team_id in loader.teams: 
            display_name = TEAM_NAMES.get(team_id, team_id)
            
            builder.button(
                text=display_name,
                callback_data=f"{action_prefix}{team_id}"
            )
    else:

        test_teams = [
            ("Авангард Омск 🦅", "Avangard Omsk"),
            ("ЦСКА Москва 🐎", "CSKA Moscow"),
            ("СКА СПб ⭐", "SKA St. Petersburg"),
        ]
        
        for team_name, team_id in test_teams:
            builder.button(
                text=team_name,
                callback_data=f"{action_prefix}{team_id}"
            )
    
    builder.adjust(2)
    

    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_seasons_keyboard(action_prefix: str = "season_") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    seasons = [
        ("Все сезоны 📊", "all"),
        ("2008/09 🏒", "809"),
        ("2009/10 🏒", "910"),
        ("2010/11 🏒", "1011"),
        ("2011/12 🏒", "1112"),
        ("2012/13 🏒", "1213"),
        ("2013/14 🏒", "1314"),
        ("2014/15 🏒", "1415"),
        ("2015/16 🏒", "1516"),
        ("2016/17 🏒", "1617"),
        ("2017/18 🏒", "1718"),
        ("2018/19 🏒", "1819"),
        ("2019/20 🏒", "1920"),
        ("2020/21 🏒", "2021"),
        ("2021/22 🏒", "2122"),
        ("2022/23 🏒", "2223"),
        ("2023/24 🏒", "2324"),
        ("2024/25 🏒", "2425"),
        ("2025/26 🏒", "2526")
    ]
    
    for season_name, season_id in seasons:
        builder.button(
            text=season_name,
            callback_data=f"{action_prefix}{season_id}"
        )
    
    builder.adjust(3)
    
    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()   
    builder.button(text="✅ Да", callback_data="confirm_yes")
    builder.button(text="❌ Нет", callback_data="confirm_no")
    
    builder.adjust(2)
    

    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_stats_options_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    options = [
        ("📊 Общая статистика", "stats_general"),
        ("⚔️ Head-to-Head", "stats_h2h"),
        ("🏠 Домашние игры", "stats_home"),
        ("✈️ Гостевые игры", "stats_away"),
        ("📈 Форма (последние 10 игр)", "stats_form"),
        ("🥅 Голы", "stats_goals")
    ]
    
    for option_text, option_id in options:
        builder.button(
            text=option_text,
            callback_data=option_id
        )
    
    builder.adjust(2)
    
    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text="⬅️ Назад", callback_data="yes")
    
    builder.adjust(2)
    

    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()



def get_back_only_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    )
    
    return builder.as_markup()

def get_table_seasons_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    
    seasons = [
        ("2008/09 🏒", "809"),
        ("2009/10 🏒", "910"),
        ("2010/11 🏒", "1011"),
        ("2011/12 🏒", "1112"),
        ("2012/13 🏒", "1213"),
        ("2013/14 🏒", "1314"),
        ("2014/15 🏒", "1415"),
        ("2015/16 🏒", "1516"),
        ("2016/17 🏒", "1617"),
        ("2017/18 🏒", "1718"),
        ("2018/19 🏒", "1819"),
        ("2019/20 🏒", "1920"),
        ("2020/21 🏒", "2021"),
        ("2021/22 🏒", "2122"),
        ("2022/23 🏒", "2223"),
        ("2023/24 🏒", "2324"),
        ("2024/25 🏒", "2425"),
        ("2025/26 🏒", "2526")
    ]
    
    for season_name, season_id in seasons:
        builder.button(
            text=season_name,
            callback_data=f"table_season_{season_id}"
        )
    
    builder.adjust(3)

    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_tops_seasons_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    seasons = [
        ("Все сезоны 📊", "all"),
        ("2008/09 🏒", "809"),
        ("2009/10 🏒", "910"),
        ("2010/11 🏒", "1011"),
        ("2011/12 🏒", "1112"),
        ("2012/13 🏒", "1213"),
        ("2013/14 🏒", "1314"),
        ("2014/15 🏒", "1415"),
        ("2015/16 🏒", "1516"),
        ("2016/17 🏒", "1617"),
        ("2017/18 🏒", "1718"),
        ("2018/19 🏒", "1819"),
        ("2019/20 🏒", "1920"),
        ("2020/21 🏒", "2021"),
        ("2021/22 🏒", "2122"),
        ("2022/23 🏒", "2223"),
        ("2023/24 🏒", "2324"),
        ("2024/25 🏒", "2425"),
        ("2025/26 🏒", "2526")
    ]
    
    for season_name, season_id in seasons:
        builder.button(
            text=season_name,
            callback_data=f"top_season_{season_id}"
        )
    
    builder.adjust(3)

    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    return builder.as_markup()

def get_tops_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    options = [
        ("🥇 Топ по победам", "top_winners"),
        ("🏆 Топ по очкам", "top_points"),
        ("📈 Топ по winrate", "top_winrate"),
        ("🥅 Топ по голам", "top_scorers"),
        ("📊 Полная таблица", "top_full_table")
    ]
    
    for option_text, option_id in options:
        builder.button(
            text=option_text,
            callback_data=option_id
        )
    
    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_plot_options_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    options = [
        ("📊 Топ победителей", "plot_winners"),
        ("🏆 Топ по очкам", "plot_points"),
        ("🥅 Топ по голам", "plot_goals"),
        ("📈 Форма команды", "plot_form"),
        ("⚔️ Сравнение голов", "plot_goals_compare")
    ]
    
    for option_text, option_id in options:
        builder.button(
            text=option_text,
            callback_data=option_id
        )
    
    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_plot_seasons_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    seasons = [
        ("Все сезоны 📊", "all"),
        ("2008/09 🏒", "809"),
        ("2009/10 🏒", "910"),
        ("2010/11 🏒", "1011"),
        ("2011/12 🏒", "1112"),
        ("2012/13 🏒", "1213"),
        ("2013/14 🏒", "1314"),
        ("2014/15 🏒", "1415"),
        ("2015/16 🏒", "1516"),
        ("2016/17 🏒", "1617"),
        ("2017/18 🏒", "1718"),
        ("2018/19 🏒", "1819"),
        ("2019/20 🏒", "1920"),
        ("2020/21 🏒", "2021"),
        ("2021/22 🏒", "2122"),
        ("2022/23 🏒", "2223"),
        ("2023/24 🏒", "2324"),
        ("2024/25 🏒", "2425"),
        ("2025/26 🏒", "2526")
    ]
    
    for season_name, season_id in seasons:
        builder.button(
            text=season_name,
            callback_data=f"plot_season_{season_id}"
        )
    
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_plots_menu"
    ))
    
    builder.adjust(3)
    return builder.as_markup()

def get_prediction_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🔮 Сделать предсказание",
        callback_data="make_prediction"
    )
    
    builder.button(
        text="📊 Статистика встреч",
        callback_data="show_h2h_stats"
    )
    
    builder.button(
        text="📈 Точность модели",
        callback_data="model_accuracy"
    )
    
    builder.row(InlineKeyboardButton(
        text="🏠 Назад в меню",
        callback_data="back_to_main_menu"
    ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_prediction_teams_keyboard(step: int = 1) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    
    if loader.teams:
        for team_id in loader.teams: 
            display_name = TEAM_NAMES.get(team_id, team_id)
            builder.button(
                text=display_name,
                callback_data=f"pred_team{step}_{team_id}"
            )
    
    builder.adjust(2)
    
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_predictions"
    ))
    
    return builder.as_markup()