from aiogram import Bot, Dispatcher, executor
from dotenv import load_dotenv

from os import environ
import asyncio

from bg_process import check_new
from sql import DataBase

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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

db = DataBase(
    environ.get('PSQL_HOST'), environ.get('PSQL_DBNAME'),
    user=environ.get('PSQL_LOGIN'), password=environ.get('PSQL_PASSWORD'),
    loop=loop
)


async def main(_):
    asyncio.create_task(check_new())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=main, skip_updates=True, loop=loop)

