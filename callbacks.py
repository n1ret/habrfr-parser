from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageCantBeDeleted

from utils import (
    get_menu, CATEGORIES, SUB_CATEGORIES,
    CATEGORIES_ENCODE, SUB_CATEGORIES_ENCODE
)
from sql import DataBase


async def menu_cb(callback: CallbackQuery):
    text, markup = get_menu()

    await callback.message.edit_text(text, reply_markup=markup)


async def categories(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id

    user = await db.get_user(tg_user)

    text = f'{("Чёрный", "Белый")[user.is_categories_whitelist]} список категорий'
    markup = InlineKeyboardMarkup()
    '''markup.add(
        InlineKeyboardButton(
            'Сменить тип списка',
            callback_data='change_categories_list_type'
        )
    )'''
    for full_category in user.categories_list:
        category, sub_category = full_category.split()
        markup.add(
            InlineKeyboardButton(
                full_category,
                callback_data=f'remove_category:{CATEGORIES_ENCODE[category]} {SUB_CATEGORIES_ENCODE[sub_category]}'
            )
        )
    markup.add(
        InlineKeyboardButton('Menu', callback_data='menu')
    )

    await callback.message.edit_text(text, reply_markup=markup)


async def change_categories_list_type(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    await db.change_category_type(tg_user)
    await categories(callback, db)


async def remove_category(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    category, sub_category = map(int, callback.data.split(':')[1].split())
    full_category = CATEGORIES[category] + ' ' + SUB_CATEGORIES[sub_category]

    user = await db.get_user(tg_user)
    if full_category not in user.categories_list:
        await callback.answer('Этой категории нет в чёрном списке')
        return
    
    await db.remove_category_from_list(tg_user, full_category)
    await categories(callback, db)


async def delete_msg(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        await callback.answer('Сообщение слишком старое', show_alert=True)
    else:
        await callback.answer('Сообщение удалено')


async def hide_category(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id

    category, sub_category = map(int, callback.data.split(':')[1].split())
    full_category = CATEGORIES[category] + ' ' + SUB_CATEGORIES[sub_category]
    user = await db.get_user(tg_user)

    if full_category in user.categories_list:
        await callback.answer('Эта категория уже в чёрном списке')
        return

    await db.add_category_to_list(tg_user, full_category)
    await callback.message.delete()
    await callback.answer('Категория скрыта')
