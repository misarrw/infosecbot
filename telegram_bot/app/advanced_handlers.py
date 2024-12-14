### Импорты
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

### Импорты из файлов
import app.database.requests as rq
import app.keyboards as kb
from app.middlewares import PermissionMiddleware


### Подключение роутеров
advanced_router = Router()


### Подключение к Middleware
advanced_router.message.outer_middleware(PermissionMiddleware())


### Редактирвоание данных
@advanced_router.message(F.text == 'Редактировать расписание')
async def edit_schedule(message: Message):
    await message.answer('ок')

@advanced_router.message(F.text == 'Изменить список группы')
async def edit_schedule(message: Message):
    await message.answer('ок')

@advanced_router.message(F.text == 'Отметить посещение')
async def edit_schedule(message: Message):
    await message.answer('ок')

'''@advanced_router.message(F.text == 'Назначить/редактировать дедлайн')
async def edit_schedule(message: Message):
    await message.answer('ок')'''

@advanced_router.callback_query(F.text == 'vip')
async def vip(callback: CallbackQuery):
    await callback.message.answer('випка')
