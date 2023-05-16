from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageCantBeDeleted

import requests


async def delete_task(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except MessageCantBeDeleted:
        await callback.answer('Сообщение слишком старое', show_alert=True)
    else:
        await callback.answer('Сообщение удалено')


async def update_task(callback: CallbackQuery):
    data = callback.data.split(':')
    task_url = data[1]

    try:
        r = requests.get(url=task_url)
    except requests.ConnectionError:
        await callback.answer('Ошибка подключения к серверу freelance.habr.com')
        return
    
    if r.status_code != requests.codes.ok:
        await callback.answer(f'{r.status_code} сервер не дал ответ')
        return
    
    soup = BeautifulSoup(r.text, 'lxml')

    title = soup.find('meta', property='og:title')

    is_publish, category, sub_category, price,
    published_date, is_marked, url, comments_count, views_count
    text = ''

    await callback.message.edit_text(text)

    await callback.answer('Данные обновлены')
