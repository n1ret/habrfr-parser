import asyncpg

import asyncio
from functools import partial
from datetime import datetime

from classes import Task, User


class DatabaseContext:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.connection = None
        self.connections_number = 0
        
    async def __aenter__(self) -> asyncpg.Connection:
        self.connections_number += 1
        if self.connection is None:
            self.connection = await asyncpg.connect(*self.args, **self.kwargs)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.connections_number -= 1
        if self.connections_number <= 0:
            await self.connection.close()


class DataBase:
    def __init__(self, host, name, user='postgres', password=None, loop=None):
        connect_dsn = f'postgresql://{user}@{host}/{name}'
        if password:
            connect_dsn += f'?password={password}'

        self.connect = partial(DatabaseContext, connect_dsn)

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.loop.run_until_complete(self.__init_db())

    async def __init_db(self):
        async with self.connect() as con:
            await con.execute("""
                CREATE TABLE IF NOT EXISTS tasks(
                    id BIGINT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    category TEXT,
                    sub_category TEXT,
                    price TEXT NOT NULL,
                    published_date TIMESTAMP NOT NULL,
                    responses_count INTEGER NOT NULL,
                    views_count INTEGER NOT NULL,
                    is_published BOOLEAN
                )
            """)

            await con.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    categories_list TEXT[],
                    is_categories_whitelist BOOLEAN DEFAULT FALSE
                )
            """)

    async def add_task(
        self, task_id: int, title: str, url: str, category: str, sub_category: str,
        price: str, published_date: datetime,
        comments_count: int, views_count: int, is_published: bool = True,
        _connection: DatabaseContext = None
    ):
        async with _connection or self.connect() as con:
            await con.execute(
                """INSERT INTO tasks(
                    id, title, url, category, sub_category, price, published_date,
                    responses_count, views_count, is_published
                ) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)""",
                task_id, title, url, category, sub_category, price, published_date,
                comments_count, views_count, is_published
            )

    async def get_task(self, task_id: int,
                       _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            row = await con.fetchrow(
                "SELECT * FROM tasks WHERE id = $1",
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

    async def add_user(self, user_id: int, username: str,
                       _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            await con.execute(
                "INSERT INTO users(id, username) VALUES($1, $2)",
                user_id, username
            )

    async def get_user(self, user_id: int,
                       _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            row = await con.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            user = None
            if row:
                user = User(*row)
        return user

    async def get_or_create_user(self, user_id: int, username: str) -> User:
        connection = self.connect()
        async with connection:
            user = await self.get_user(user_id, connection)
            if not user:
                await self.add_user(user_id, username, connection)
                user = await self.get_user(user_id, connection)
            return user
    
    async def get_users_ids(self, category: str) -> list[int]:
        async with self.connect() as con:
            rows = await con.fetch(
                "SELECT id FROM users WHERE $1 != all(categories_list)",
                category
            )

        return [row.get('id') for row in rows]

    async def add_category_to_list(self, user_id: int, category: str):
        async with self.connect() as con:
            await con.execute(
                "UPDATE users SET categories_list = array_append(categories_list, $2) WHERE id = $1",
                user_id, category
            )
    
    async def remove_category_from_list(self, user_id: int, category: str):
        async with self.connect() as con:
            await con.execute(
                "UPDATE users SET categories_list = array_remove(categories_list, $2) WHERE id = $1",
                user_id, category
            )
    
    async def change_category_type(self, user_id: int):
        async with self.connect() as con:
            await con.execute(
                "UPDATE users SET is_categories_whitelist = NOT is_categories_whitelist WHERE id = $1",
                user_id
            )
