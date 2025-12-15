import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.data_loader import loader
from app.handlers import router

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN не найден в переменных окружения!")
    print("⚠️  Убедитесь, что вы создали файл .env с TELEGRAM_TOKEN=ваш_токен")
    exit(1)

async def main():
    print("📊 Загрузка данных...")
    if not loader.load():
        print("❌ Не удалось загрузить данные! Проверьте файл data/KHL_v1.csv")
        return
    
    print(f"✅ Данные загружены: {len(loader.df)} игр, {len(loader.teams)} команд")
    
    from app.prediction_engine import PredictionEngine
    from app.stats_calculator import StatsCalculator
    
    global prediction_engine, calculator
    prediction_engine = PredictionEngine(loader.df)
    calculator = StatsCalculator(loader.df)
    
    from app import handlers
    handlers.prediction_engine = prediction_engine
    handlers.calculator = calculator
    
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(router)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)   
        print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")      
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен по запросу пользователя")
    except Exception as e:
        print(f"❌ Возникла ошибка при работе бота: {e}")
    finally:
        await bot.session.close()
        print("🔌 Сессия бота закрыта")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Бот остановлен")