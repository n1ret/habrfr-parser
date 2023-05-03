from aiogram.dispatcher.middlewares import BaseMiddleware


class DBMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db
        super().__init__()

    async def on_pre_process_update(
        self, obj, data, *_
    ):
        data['db'] = self.db
    
    async def on_post_process_update(
        self, obj, arr, data, *_
    ):
        data.pop('db')

    async def on_pre_process_callback_query(
        self, obj, data, *_
    ):
        data['db'] = self.db
    
    async def on_post_process_callback_query(
        self, obj, arr, data, *_
    ):
        data.pop('db')

    async def on_pre_process_message(
        self, obj, data, *_
    ):
        data['db'] = self.db
    
    async def on_post_process_message(
        self, obj, arr, data, *_
    ):
        data.pop('db')

    async def trigger(self, *args):
        await super().trigger(*args)

