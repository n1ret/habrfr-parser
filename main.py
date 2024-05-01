import asyncio
import logging
from contextlib import asynccontextmanager
from os import getenv

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Update
from dotenv import load_dotenv
from fastapi import FastAPI

from bg_process import check_new
from callbacks import (
    categories_menu,
    change_categories_list_type,
    delete_msg,
    distribution,
    hide_category,
    menu_cb,
    sub_categories_menu,
    toggle_category,
    toggle_sub_category,
    toggle_subscription,
)
from messages import distribution_message, menu, start
from middlewares import DBMiddleware
from sql import DataBase
from states import Distribution

load_dotenv()
logging.basicConfig(level=logging.WARNING, format='%(levelname)-8s[%(asctime)s] %(message)s')

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
else:
    loop = asyncio.get_event_loop()

BOT_TOKEN = getenv('TOKEN')
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = getenv('URL') + WEBHOOK_PATH
PEM_CERT = getenv('PEM_CERT')

if not all(BOT_TOKEN):
    if not BOT_TOKEN:
        print("Enter bot token at .env(TOKEN=<bot token>)")

    exit(-1)

bot = Bot(token=BOT_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = DataBase(
    getenv('PSQL_HOST'), getenv('PSQL_DBNAME'),
    user=getenv('PSQL_LOGIN'), password=getenv('PSQL_PASSWORD'),
    loop=loop
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info != WEBHOOK_URL:
        with open(PEM_CERT) as f:
            await bot.set_webhook(url=WEBHOOK_URL, certificate=f)
    asyncio.create_task(check_new(bot, db))

    yield

    session = await bot.get_session()
    await session.close()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


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

    uvicorn.run(app, host="127.0.0.1", port=9999, log_level=logging.WARNING)
