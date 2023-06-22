from aiogram import types

from sql import DataBase

from utils import get_menu


async def start(message: types.Message, db: DataBase):
    tg_user = message.from_user

    if tg_user.is_bot:
        return

    await db.get_or_create_user(tg_user.id, tg_user.username)

    await message.answer('Вы добавлены в рассылку\n/menu для управления рассылкой')


async def menu(message: types.Message):
    text, markup = get_menu()

    await message.answer(text, reply_markup=markup)
