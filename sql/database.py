from .modules import DBBase, DBTasks, DBUsers, DBCategories


class DataBase(DBTasks, DBUsers, DBCategories, DBBase):
    async def init_db(self):
        async with self.connect() as con:
            await con.execute("""
                CREATE TABLE IF NOT EXISTS categories(
                    id INTEGER PRIMARY KEY,
                    category_name TEXT,
                    sub_category_name TEXT,
                    category_id INTEGER,
                    sub_category_id INTEGER,
                    UNIQUE (category_name, sub_category_name)
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
                    is_categories_whitelist BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_subscribed BOOLEAN DEFAULT TRUE
                );
                CREATE TABLE IF NOT EXISTS users_categories(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id),
                    category_id INTEGER REFERENCES categories(id)
                );

                CREATE OR REPLACE FUNCTION public.xor (a boolean, b boolean) returns boolean immutable language sql AS
                $$
                SELECT (a and not b) or (b and not a);
                $$
            """)
        
        return await super().init_db()
