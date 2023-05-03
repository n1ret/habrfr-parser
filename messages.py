from aiogram import types

from sql import DataBase


async def start(message: types.Message, db: DataBase):
    tg_user = message.from_user

    await db.get_or_create_user(tg_user.id, tg_user.username)

    await message.answer('Вы добавлены в рассылку')
