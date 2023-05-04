from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    task_id: int
    title: str
    url: str
    category: str
    sub_category: str
    price: str
    published_date: datetime
    comments_count: int
    views_count: int
    is_published: bool


@dataclass
class User:
    user_id: int
    username: str
    categories: list[str]
