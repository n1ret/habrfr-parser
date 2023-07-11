from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from os import environ
import asyncio
import logging

from messages import menu, start, distribution_message
from callbacks import (
    menu_cb, delete_msg, change_categories_list_type, toggle_category,
    hide_category, categories_menu, sub_categories_menu, toggle_sub_category,
    distribution, toggle_subscription
)
from bg_process import check_new
from sql import DataBase
from middlewares import DBMiddleware
from states import Distribution

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(levelname)-8s[%(asctime)s] %(message)s')

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
else:
    loop = asyncio.get_event_loop()

BOT_TOKEN = environ.get('TOKEN')

if not all(BOT_TOKEN):
    if not BOT_TOKEN:
        print("Enter bot token at .env(TOKEN=<bot token>)")

    exit(-1)

bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = DataBase(
    environ.get('PSQL_HOST'), environ.get('PSQL_DBNAME'),
    user=environ.get('PSQL_LOGIN'), password=environ.get('PSQL_PASSWORD'),
    loop=loop
)


async def main(_):
    asyncio.create_task(check_new(bot, db))


if __name__ == '__main__':
    dp.middleware.setup(DBMiddleware(db))

    dp.register_message_handler(menu, commands=['menu'], state='*')
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(distribution_message, state=Distribution.message)

    dp.register_callback_query_handler(menu_cb, text='menu', state='*')
    dp.register_callback_query_handler(delete_msg, text='delete', state='*')
    dp.register_callback_query_handler(hide_category, text_startswith='hide_category:', state='*')
    dp.register_callback_query_handler(categories_menu, text='categories')
    dp.register_callback_query_handler(change_categories_list_type, text='change_categories_list_type')
    dp.register_callback_query_handler(sub_categories_menu, text_startswith='sub_categories:')
    dp.register_callback_query_handler(toggle_category, text_startswith='toggle_category:')
    dp.register_callback_query_handler(toggle_sub_category, text_startswith='toggle_sub_category:')
    dp.register_callback_query_handler(distribution, text='distribution')
    dp.register_callback_query_handler(toggle_subscription, text='toggle_subscription')

    executor.start_polling(dp, on_startup=main, skip_updates=True, loop=loop)
