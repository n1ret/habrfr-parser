from requests import get
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from os import environ

from sql import DataBase

load_dotenv()
db = DataBase(
    environ.get('PSQL_HOST'), environ.get('PSQL_DBNAME'),
    user=environ.get('PSQL_LOGIN'), password=environ.get('PSQL_PASSWORD')
)


async def parse():
    r = get('https://freelance.habr.com/tasks')
    soup = BeautifulSoup(r.text, 'lxml')

    categories_list = []
    for i, category in enumerate(soup.find_all('li', {'class': 'category-group__folder'})):
        category_name = category.find(
            'span', {'class': 'link_dotted js-toggle'}
        ).text.strip()

        for u, sub_category in enumerate(category.find_all('span', {'class': 'checkbox__label'})):
            sub_category_name = sub_category.text.strip()
            categories_list.append(
                (len(categories_list), category_name, sub_category_name, i, u)
            )

    await db.write_categories(categories_list)
