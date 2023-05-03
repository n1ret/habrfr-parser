from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    task_id: int
    title: str
    category: str
    sub_category: str
    price: str
    published_date: datetime
    comments_count: int
    views_count: int


@dataclass
class User:
    user_id: int
    username: str
    categories: list[str]
