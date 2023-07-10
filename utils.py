from aiogram import types


def get_menu():
    text = 'Menu'
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Категории', callback_data='categories')
    ).add(
        types.InlineKeyboardButton('Закрыть', callback_data='delete')
    )
    return text, markup
