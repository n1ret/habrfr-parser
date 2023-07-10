from aiogram import types
from aiogram.dispatcher import FSMContext

from sql import DataBase

from utils import get_menu


async def start(message: types.Message, db: DataBase):
    tg_user = message.from_user

    if tg_user.is_bot:
        return

    await db.get_or_create_user(tg_user.id, tg_user.username)

    await message.answer('Вы добавлены в рассылку\n/menu для управления рассылкой')


async def menu(message: types.Message, db: DataBase, state: FSMContext):
    await state.finish()

    text, markup = await get_menu(db, message.from_user)

    await message.answer(text, reply_markup=markup)


async def distribution_message(message: types.Message, db: DataBase, state: FSMContext):
    await state.finish()

    tg_user = message.from_user.id

    for user_id in await db.get_all_users_ids(tg_user):
        await message.send_copy(user_id)

    text = 'Сообщения отправлены'
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Menu', callback_data='menu')
    )
    await message.answer(text, reply_markup=markup)
