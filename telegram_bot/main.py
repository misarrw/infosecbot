### Импорты
import asyncio
from aiogram import Bot, Dispatcher
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler


### Импорт из файлов
from app.handlers import router
from app.deadline_handlers import deadline_router
from app.advanced_handlers import advanced_router
from app.database.models import async_main
from app.middlewares import DDMiddleware


### Стиль логгинга
style = logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s'
)


### Инициализация логера модуля
logger = logging.getLogger(__name__)


### Начало работы с ботом
async def main() -> None:
    """Основная функция, подключение к базе данных, подключение к боту,
    инициализация диспетчера

    :return: None
    """
    ### подключение к бд
    await async_main()

    ### подключение к боту
    bot = Bot(token='7946627017:AAEZpHwYuXV5syytjvclO2OQ_49S7zVRp7c')

    ### инициализация диспетчера и включение обработчиков
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(advanced_router)
    dp.include_router(deadline_router)


    ### инициализация скедулера
    scheduler = AsyncIOScheduler(timezone = 'Europe/Moscow')
    scheduler.start()


    dp.update.middleware.register(DDMiddleware(scheduler))


    ### включение бота
    await dp.start_polling(bot)


### обработка исключений
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Black out') # убирает ошибку KeyboardInterrupt в терминале
