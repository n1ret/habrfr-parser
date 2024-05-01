from ..classes import User
from .base import DatabaseContext, DBBase


class DBUsers(DBBase):
    async def add_user(self, user_id: int, username: str,
                       _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            await con.execute(
                "INSERT INTO users(id, username) VALUES($1, $2)",
                user_id, username
            )
    
    async def get_unavailable(self) -> list[int]:
        async with self.connect() as con:
            rows = await con.fetch(
                "SELECT id FROM users WHERE is_available = 'false'"
            )

        return [row.get('id') for row in rows]

    async def set_available(self, user_id: int, value: bool,
                            _connection: DatabaseContext = None):
        async with _connection or self.connect() as con:
            await con.execute(
                "UPDATE users SET is_available = $2 WHERE id = $1",
                user_id, value
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
    
    async def get_all_users_ids(self, user_id: int) -> list[int]:
        """return ids of all users without user_id

        Args:
            user_id (int): id of the user who is excluded

        Returns:
            list[int]: user ids
        """

        async with self.connect() as con:
            rows = await con.fetch(
                "SELECT id FROM users WHERE id != $1",
                user_id
            )

        return [row.get('id') for row in rows]

    async def get_users_ids(self, category: str, sub_category: str) -> list[int]:
        async with self.connect() as con:
            rows = await con.fetch(
                """SELECT u.id FROM users u WHERE u.is_subscribed AND (
                    xor(
                        u.id NOT IN (
                            SELECT distinct(uc.user_id) FROM users_categories uc
                            INNER JOIN categories c ON uc.category_id = c.id
                            WHERE c.category_name = $1 AND c.sub_category_name = $2
                        ),
                        u.is_categories_whitelist
                    ) OR
                    NOT EXISTS(
                        SELECT 1 FROM users_categories uc WHERE uc.user_id = u.id
                    ) AND u.is_categories_whitelist
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
    
    async def toggle_subscription(self, user_id: int):
        async with self.connect() as con:
            await con.execute(
                "UPDATE users SET is_subscribed = NOT is_subscribed WHERE id = $1",
                user_id
            )
