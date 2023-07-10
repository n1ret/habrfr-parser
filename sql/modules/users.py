from .base import DatabaseContext, DBBase
from ..classes import User


class DBUsers(DBBase):
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
    
    async def get_users_categories(self, user_id: int) -> list[tuple[str, str, int, int]]:
        async with self.connect() as con:
            rows = await con.fetch(
                """SELECT c.id, c.category_name, c.sub_category_name, c.category_id, c.sub_category_id
                FROM categories c INNER JOIN users_categories uc ON c.id = uc.category_id
                WHERE uc.user_id = $1""",
                user_id
            )

        return rows

    async def get_users_ids(self, category: str, sub_category: str) -> list[int]:
        async with self.connect() as con:
            rows = await con.fetch(
                """SELECT id FROM users WHERE (
                        id != all(
                        SELECT distinct(uc.user_id) FROM users_categories uc
                        INNER JOIN categories c ON uc.category_id = c.id
                        WHERE c.category_name = $1 AND c.sub_category_name = $2
                    )::integer + is_categories_whitelist::integer = 1
                )""",
                category, sub_category
            )

        return [row.get('id') for row in rows]

    async def change_list_type(self, user_id: int):
        async with self.connect() as con:
            await con.execute(
                "UPDATE users SET is_categories_whitelist = NOT is_categories_whitelist WHERE id = $1",
                user_id
            )
