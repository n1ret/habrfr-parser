import asyncpg

import asyncio
from functools import partial


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


class DBBase:
    def __init__(self, host, name, user='postgres', password=None, loop=None):
        connect_dsn = f'postgresql://{user}@{host}/{name}'
        if password:
            connect_dsn += f'?password={password}'

        self.connect = partial(DatabaseContext, connect_dsn)

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.loop.run_until_complete(self.init_db())

    async def init_db(self):
        pass
