from aiogram.types import CallbackQuery


async def delete_task(callback: CallbackQuery):
    await callback.message.delete()

    await callback.answer('Сообщение удалено')
