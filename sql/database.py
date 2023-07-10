from .modules import DBBase, DBTasks, DBUsers, DBCategories


class DataBase(DBTasks, DBUsers, DBCategories, DBBase):
    async def __init_db(self):
        async with self.connect() as con:
            await con.execute("""
                CREATE TABLE IF NOT EXISTS categories(
                    id INTEGER PRIMARY KEY,
                    category_name TEXT,
                    sub_category_name TEXT,
                    category_id INTEGER,
                    sub_category_id INTEGER
                );
                CREATE TABLE IF NOT EXISTS tasks(
                    id BIGINT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    category_id INTEGER REFERENCES categories(id),
                    price TEXT NOT NULL,
                    published_date TIMESTAMP NOT NULL,
                    responses_count INTEGER NOT NULL,
                    views_count INTEGER NOT NULL,
                    is_published BOOLEAN
                );
                CREATE TABLE IF NOT EXISTS users(
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    is_categories_whitelist BOOLEAN DEFAULT FALSE
                );
                CREATE TABLE IF NOT EXISTS users_categories(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id),
                    category_id INTEGER REFERENCES categories(id)
                )
            """)
