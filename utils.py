from aiogram import types

from sql import DataBase


async def get_menu(db: DataBase, tg_user: types.User):
    user = await db.get_user(tg_user.id)

    text = 'Menu'
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Категории', callback_data='categories')
    )
    if user.is_admin:
        markup.add(
            types.InlineKeyboardButton('Рассылка', callback_data='distribution')
        )
    markup.add(
        types.InlineKeyboardButton('Закрыть', callback_data='delete')
    )
    return text, markup
