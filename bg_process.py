from aiogram import Bot

from asyncio import sleep, run
import requests
from datetime import datetime

from sql import DataBase


async def check_new(bot: Bot, db: DataBase):
    while True:
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get("https://freelance.habr.com/tasks?page=1&a=1", headers=headers)
        tasks: list[dict] = r.json()

        tasks_args: list[tuple] = []
        for task in tasks:
            (
                task_id, title, is_publish, category, sub_category, price,
                published_date, is_marked, url, comments_count, views_count
            ) = task.values()

            published_date = datetime.fromisoformat(published_date)
            published_date = published_date.replace(tzinfo=None) - published_date.tzinfo.utcoffset(None)

            args = (
                task_id, title, category, sub_category, price,
                published_date, comments_count, views_count
            )

            tasks_args.append(args)
        
        are_new_tasks = await db.create_or_update_tasks(tasks_args)

        for is_new, task in zip(are_new_tasks, tasks_args):
            if is_new:
                (
                    task_id, title, category, sub_category, price,
                    published_date, comments_count, views_count
                ) = task
                for user in await db.get_users_ids():
                    await bot.send_message(
                        user,
                        f'Новая задача: <b>{title}</b>\n'
                        f'Цена: <i>{price}</i>\n'
                        f'Количество отзывов: {comments_count}\n'
                        f'{category} {sub_category}'
                    )
        await sleep(60)
