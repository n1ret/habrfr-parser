from aiogram import Bot, types

from asyncio import sleep
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
                text = (
                    f'Новая задача: <b>{title}</b>\n'
                    f'Цена: <i>{price}</i>\n'
                    f'Отзывов/просмотров: {comments_count}/{views_count}\n'
                    f'{category} {sub_category}'
                )
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(
                        '❌ Удалить',
                        callback_data='delete'
                    ),
                    types.InlineKeyboardButton(
                        '🔗 Ссылка',
                        f'https://freelance.habr.com/tasks/{task_id}'
                    )
                )

                for user in await db.get_users_ids():
                    await bot.send_message(
                        user, text,
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
        await sleep(60)
