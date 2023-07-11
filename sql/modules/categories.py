from requests import get
from bs4 import BeautifulSoup

from .base import DBBase
from ..classes import Category


class DBCategories(DBBase):
    async def init_db(self):
        async with self.connect() as con:
            if not await con.fetchval(
                "SELECT EXISTS(SELECT 1 FROM categories LIMIT 1)"
            ):
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

                await self.write_categories(categories_list)

        return await super().init_db()

    async def write_categories(self, categories: list[tuple[int, str, str, int, int]]):
        async with self.connect() as con:
            await con.executemany(
                """
                INSERT INTO categories (id, category_name, sub_category_name, category_id, sub_category_id)
                VALUES ($1, $2, $3, $4, $5)
                """,
                categories
            )
    
    async def get_category_id(self, category: str, sub_category: str) -> int:
        async with self.connect() as con:
            category_id = await con.fetchval(
                "SELECT id FROM categories WHERE category_name=$1 AND sub_category_name=$2",
                category, sub_category
            )

        return category_id
    
    async def get_category(self, category_id: int):
        async with self.connect() as con:
            category = await con.fetchrow(
                "SELECT * FROM categories WHERE id=$1",
                category_id
            )

        return Category(category)

    async def is_full_category(self, user_id: int, category: str) -> bool:
        async with self.connect() as con:
            is_full: bool = await con.fetchval(
                """SELECT (SELECT count(*) FROM categories WHERE category_name = $2) =
                (
                    SELECT count(*) FROM categories c
                    INNER JOIN users_categories uc ON c.id = uc.category_id
                    WHERE c.category_name = $2 AND uc.user_id = $1
                )""",
                user_id, category
            )

        return is_full

    async def get_categories(self, user_id: int) -> list[tuple[str, bool, bool]]:
        async with self.connect() as con:
            categories = await con.fetch(
                """SELECT DISTINCT(cf.category_name), (
                    (SELECT count(*) FROM categories WHERE category_name = cf.category_name) =
                    (
                        SELECT count(*) FROM categories c
                        INNER JOIN users_categories uc ON c.id = uc.category_id
                        WHERE c.category_name = cf.category_name AND uc.user_id = $1
                    )
                ), EXISTS(
                    SELECT 1 FROM categories c
                    INNER JOIN users_categories uc ON c.id = uc.category_id
                    WHERE c.category_name = cf.category_name AND uc.user_id = $1
                    LIMIT 1
                )
                FROM categories cf""",
                user_id
            )

        return categories

    async def get_sub_categories(self, user_id: int, category: str) -> list[tuple[int, bool]]:
        async with self.connect() as con:
            sub_categories = await con.fetch(
                """SELECT c.sub_category_name, uc.user_id = $1 FROM categories c
                LEFT JOIN users_categories uc ON c.id = uc.category_id
                WHERE c.category_name = $2""",
                user_id, category
            )

        return sub_categories
    
    async def toggle_category(self, user_id: int, category: str):
        async with self.connect() as con:
            await con.execute(
                f"""DO $$ BEGIN
                IF (SELECT count(*) FROM categories WHERE category_name = '{category}') =
                (
                    SELECT count(*) FROM categories c
                    INNER JOIN users_categories uc ON c.id = uc.category_id
                    WHERE c.category_name = '{category}' AND uc.user_id = '{user_id}'
                ) THEN
                    DELETE FROM users_categories uc USING categories c
                    WHERE uc.user_id = '{user_id}' AND uc.category_id = c.id AND c.category_name = '{category}';
                ELSE
                    INSERT INTO users_categories(user_id, category_id)
                    SELECT '{user_id}', c.id
                    FROM categories c LEFT JOIN users_categories uc ON c.id = uc.category_id
                    WHERE c.category_name = '{category}' AND (uc.user_id != '{user_id}' OR uc.user_id IS NULL);
                END IF;
                END $$"""
            )
    
    async def toggle_sub_category(self, user_id: int, category_id: int):
        async with self.connect() as con:
            await con.execute(
                f"""DO $$ BEGIN
                IF EXISTS(
                    SELECT 1 FROM users_categories
                    WHERE user_id = '{user_id}' AND category_id = '{category_id}'
                ) THEN
                    DELETE FROM users_categories
                    WHERE user_id = '{user_id}' AND category_id = '{category_id}';
                ELSE
                    INSERT INTO users_categories(user_id, category_id)
                    VALUES ('{user_id}', '{category_id}');
                END IF;
                END $$"""
            )
