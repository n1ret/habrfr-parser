from dataclasses import dataclass
from datetime import datetime


class Category:
    def __init__(self, args: tuple[int, str, str, int, int]) -> None:
        (
            self.id,
            self.category_name,
            self.sub_category_name,
            self.category_id,
            self.sub_category_id
        ) = args
    
    def __repr__(self) -> str:
        return (
            f'{self.category_id} {self.category_name} '
            f'{self.sub_category_id} {self.sub_category_name}'
        )
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.category_name + ' ' + self.sub_category_name == __value
        elif isinstance(__value, int):
            return self.id == __value
        else:
            raise TypeError(f'Category cant be compared to {type(__value)}')


@dataclass
class Task:
    task_id: int
    title: str
    url: str
    category: Category
    price: str
    published_date: datetime
    comments_count: int
    views_count: int
    is_published: bool


@dataclass
class User:
    user_id: int
    username: str
    is_categories_whitelist: bool

    categories_list: list[Category] = None

    async def parse_categories(self, db):
        self.categories_list = []
        for row in await db.get_users_categories(self.user_id):
            self.categories_list.append(Category(row))
