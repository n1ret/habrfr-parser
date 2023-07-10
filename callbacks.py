from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageCantBeDeleted

from utils import (
    get_menu
)
from sql import DataBase


async def menu_cb(callback: CallbackQuery):
    text, markup = get_menu()

    await callback.message.edit_text(text, reply_markup=markup)


async def categories_menu(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    user = await db.get_user(tg_user)

    text = f'{("Чёрный", "Белый")[user.is_categories_whitelist]} список категорий'
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            'Сменить тип списка',
            callback_data='change_categories_list_type'
        )
    )

    for category_name, is_full in await db.get_categories(tg_user):
        btn_text = category_name + ('🟢' if is_full else '⚫️')
        markup.add(
            InlineKeyboardButton(
                btn_text,
                callback_data=f'sub_categories:{category_name}'
            )
        )
    markup.add(
        InlineKeyboardButton('Menu', callback_data='menu')
    )

    await callback.message.edit_text(text, reply_markup=markup)


async def change_categories_list_type(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    await db.change_list_type(tg_user)
    await categories_menu(callback, db)


async def sub_categories_menu(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    category_name = callback.data.split(':')[1]
    
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Back', callback_data='categories'),
        InlineKeyboardButton(
            '🟢' if await db.is_full_category(tg_user, category_name) else '⚫️',
            callback_data=f'toggle_category:{category_name}'
        )
    )
    
    for sub_category, is_selected in await db.get_sub_categories(tg_user, category_name):
        btn_text = sub_category + ('🟢' if is_selected else '⚫️')
        markup.add(
            InlineKeyboardButton(
                btn_text,
                callback_data=f'toggle_sub_category:{await db.get_category_id(category_name, sub_category)}'
            )
        )

    await callback.message.edit_reply_markup(reply_markup=markup)


async def toggle_category(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    category_name = callback.data.split(':')[1]
    
    await db.toggle_category(tg_user, category_name)

    await sub_categories_menu(callback, db)


async def toggle_sub_category(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    category_id = int(callback.data.split(':')[1])
    category = await db.get_category(category_id)

    await db.toggle_sub_category(tg_user, category_id)

    callback.data = f':{category.category_name}'
    await sub_categories_menu(callback, db)


async def delete_msg(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        await callback.answer('Сообщение слишком старое', show_alert=True)
    else:
        await callback.answer('Сообщение удалено')


async def hide_category(callback: CallbackQuery, db: DataBase):
    tg_user = callback.from_user.id
    user = await db.get_user(tg_user)
    await user.parse_categories(db)

    category_id = int(callback.data.split(':')[1])
    is_category_in_list = category_id in user.categories_list

    if not user.is_categories_whitelist:
        if is_category_in_list:
            await callback.answer('Эта категория уже в чёрном списке')
            return
    else:
        if not is_category_in_list:
            await callback.answer('Этой категории нет в белом списке')
            return

    await db.toggle_sub_category(tg_user, category_id)

    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        pass

    await callback.answer('Категория скрыта')
