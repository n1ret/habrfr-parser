from datetime import datetime

from .base import DatabaseContext, DBBase
from ..classes import Task


class DBTasks(DBBase):
    async def add_task(
        self, task_id: int, title: str, url: str, category: str, sub_category: str,
        price: str, published_date: datetime,
        comments_count: int, views_count: int, is_published: bool = True,
        _connection: DatabaseContext = None
    ):
        async with _connection or self.connect() as con:
            await con.execute(
                """INSERT INTO tasks(
                    id, title, url, category_id, price, published_date,
                    responses_count, views_count, is_published
                ) SELECT $1, $2, $3, c.id, $6, $7, $8, $9, $10
                FROM categories c WHERE category_name=$4 AND sub_category_name=$5""",
                task_id, title, url, category, sub_category, price, published_date,
                comments_count, views_count, is_published
            )

    async def get_task(self, task_id: int,
                       _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            row = await con.fetchrow(
                """
                SELECT
                t.id, t.title, t.url,
                (c.category_name, c.sub_category_name, c.category_id, c.sub_category_id),
                t.price, t.published_date, t.responses_count, t.views_count, t.is_published
                FROM tasks t INNER JOIN categories c ON t.category_id = c.id
                WHERE t.id = $1
                """,
                task_id
            )
            task = None
            if row:
                task = Task(*row)
        return task

    async def create_or_ignore_tasks(
        self, tasks: list[tuple[int, str, str, str, str, str, datetime, int, int, bool]]
    ):
        """Create or update task

        Returns:
            list[
                True: Task created
                False: Task ignored
            ]
        """

        is_new = []
        connection = self.connect()
        async with connection:
            for task in tasks:
                (
                    task_id, title, url, category, sub_category,
                    price, published_date,
                    comments_count, views_count, is_published
                ) = task

                is_task_not_exists = await self.get_task(task_id, connection) is None
                is_new.append(is_task_not_exists)
                if is_task_not_exists:
                    await self.add_task(
                        task_id, title, url, category, sub_category,
                        price, published_date,
                        comments_count, views_count, is_published,
                        connection
                    )

        return is_new
