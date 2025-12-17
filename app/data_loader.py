import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

class DataLoader:
    
    def __init__(self, data_path="data/KHL_v1.csv"):
        self.data_path = data_path
        self.df = None
        self.teams = []
        self.seasons = []
        self.raw_row_count = 0
        self.processed_row_count = 0
    
    def load(self):
        try:
            logger.info(f"Попытка загрузить файл: {self.data_path}")
            
            # Загружаем с исправлением BOM и обработкой ошибок
            self.df = pd.read_csv(
                self.data_path, 
                encoding='utf-8-sig',  # Для обработки BOM символа
                on_bad_lines='warn',
                skipinitialspace=True
            )
            
            # Убираем BOM символы из названий колонок
            self.df.columns = [col.strip().replace('\ufeff', '') for col in self.df.columns]
            
            self.raw_row_count = len(self.df)
            logger.info(f"Загружено строк: {self.raw_row_count}")
            
            # Проверяем наличие необходимых колонок
            required_columns = ['HG', 'AG', 'HOMETEAM', 'AWAYTEAM', 'SEASON']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            
            if missing_columns:
                logger.error(f"Отсутствуют колонки: {missing_columns}")
                logger.info(f"Доступные колонки: {list(self.df.columns)}")
                return False
            
            # ОЧИСТКА ДАННЫХ
            self._clean_data()
            
            # Проверяем типы данных
            logger.info("Типы данных после очистки:")
            for col in ['SEASON', 'HOMETEAM', 'AWAYTEAM', 'HG', 'AG']:
                if col in self.df.columns:
                    logger.info(f"  {col}: {self.df[col].dtype}")
            
            # Создаем колонку SCORE
            self.df['SCORE'] = self.df['HG'].astype(str).str.strip() + ':' + self.df['AG'].astype(str).str.strip()
            
            # Проверяем уникальность команд
            self._get_metadata()
            
            self.processed_row_count = len(self.df)
            logger.info(f"✅ Данные загружены успешно")
            logger.info(f"📊 Команд: {len(self.teams)}")
            logger.info(f"📅 Сезонов: {len(self.seasons)}")
            logger.info(f"🎯 Сезоны: {sorted(self.seasons)}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки: {e}", exc_info=True)
            return False
    
    def _clean_data(self):
        """Очистка данных"""
        logger.info("🧹 Очистка данных...")
        
        # 1. Очищаем сезоны - оставляем только числовые значения 4-значных сезонов
        if 'SEASON' in self.df.columns:
            # Преобразуем к строке и убираем пробелы
            self.df['SEASON'] = self.df['SEASON'].astype(str).str.strip()
            
            # Фильтруем только корректные сезоны (4 цифры или формат типа "2526")
            season_pattern = r'^\d{4}$'  # Только 4 цифры
            valid_seasons = self.df['SEASON'].str.match(season_pattern)
            
            # Находим проблемные строки
            invalid_rows = self.df[~valid_seasons]
            if len(invalid_rows) > 0:
                logger.warning(f"Найдено {len(invalid_rows)} строк с некорректными сезонами:")
                unique_invalid = invalid_rows['SEASON'].unique()[:10]  # Первые 10
                logger.warning(f"  Некорректные значения: {list(unique_invalid)}")
                
                # Удаляем строки с некорректными сезонами
                self.df = self.df[valid_seasons].copy()
                logger.info(f"  Удалено строк: {len(invalid_rows)}")
            
            # Преобразуем сезоны в числовой формат для сортировки
            self.df['SEASON'] = self.df['SEASON'].astype(int)
        
        # 2. Очищаем названия команд
        for col in ['HOMETEAM', 'AWAYTEAM', 'WINNER']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
        
        # 3. Преобразуем числовые колонки
        numeric_columns = ['HG', 'AG', 'DAY', 'MONTH', 'YEAR']
        for col in numeric_columns:
            if col in self.df.columns:
                # Заменяем пустые строки на NaN и преобразуем
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        logger.info(f"После очистки осталось строк: {len(self.df)}")
    
    def _get_metadata(self):
        try:
            # Получаем уникальные команды
            home_teams = self.df['HOMETEAM'].unique()
            away_teams = self.df['AWAYTEAM'].unique()

            all_teams_set = set(home_teams) | set(away_teams)
            self.teams = sorted([team for team in all_teams_set if isinstance(team, str) and team.strip()])
            
            logger.info(f"Найдено команд: {len(self.teams)}")
            logger.info(f"Примеры команд (первые 10): {self.teams[:10]}")

            # Получаем уникальные сезоны
            self.seasons = sorted(self.df['SEASON'].unique())
            logger.info(f"Найдено сезонов: {len(self.seasons)}")
            logger.info(f"Сезоны: {self.seasons}")
            
        except Exception as e:
            logger.error(f"Ошибка получения метаданных: {e}", exc_info=True)
    
    def get_team_stats(self, team_name):
        if self.df is None:
            logger.error("Данные не загружены")
            return {}
        
        try:
            # Ищем команду (с учетом возможных различий в написании)
            team_name_clean = str(team_name).strip()
            games = self.df[
                (self.df['HOMETEAM'].str.strip() == team_name_clean) | 
                (self.df['AWAYTEAM'].str.strip() == team_name_clean)
            ]
            
            if len(games) == 0:
                logger.warning(f"Не найдено игр для команды: {team_name}")
                return {}
            
            wins = len(games[games['WINNER'].str.strip() == team_name_clean])
            total = len(games)
            
            stats = {
                'team': team_name,
                'games': int(total),
                'wins': int(wins),
                'losses': int(total - wins),
                'win_rate': f"{(wins/total*100):.1f}%" if total > 0 else "0.0%"
            }
            
            logger.info(f"Статистика для {team_name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}", exc_info=True)
            return {}
    
    def get_season_games(self, season):
        """Получить игры определенного сезона"""
        if self.df is None:
            return pd.DataFrame()
        
        try:
            season_games = self.df[self.df['SEASON'] == int(season)]
            logger.info(f"Игр в сезоне {season}: {len(season_games)}")
            return season_games
        except:
            return pd.DataFrame()
    
    def get_seasons_list(self):
        """Получить список доступных сезонов"""
        if self.df is None:
            return []
        return [int(s) for s in self.seasons]
    
    def get_teams_list(self):
        """Получить список команд"""
        if self.df is None:
            return []
        return self.teams
    
    def get_games_by_team_and_season(self, team_name, season=None):
        """Получить игры команды по сезону"""
        if self.df is None:
            return pd.DataFrame()
        
        try:
            team_name_clean = str(team_name).strip()
            mask = (self.df['HOMETEAM'].str.strip() == team_name_clean) | (self.df['AWAYTEAM'].str.strip() == team_name_clean)
            
            if season:
                mask = mask & (self.df['SEASON'] == int(season))
            
            games = self.df[mask]
            return games
            
        except Exception as e:
            logger.error(f"Ошибка получения игр: {e}")
            return pd.DataFrame()

loader = DataLoader("data/KHL_v1.csv")

# Пытаемся загрузить данные при импорте
try:
    success = loader.load()
    if success:
        print("✅ Данные успешно загружены при импорте")
    else:
        print("❌ Не удалось загрузить данные при импорте")
except Exception as e:
    print(f"⚠️ Ошибка при загрузке данных: {e}")