from aiogram import executor, types, Dispatcher
from aiogram.utils import executor
from config import TOKEN
from create_bot import dp
from data_base import sqlite_db
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

async def on_startup(_):
	print('Бот вышел в онлайн')
	sqlite_db.sql_start()
	


from handlers import client, admin, other, internat


admin.register_handlers_admin(dp)
internat.register_handlers_internat(dp)
client.register_handlers_client(dp)
#other.register_handlers_other(dp)


dp.middleware.setup(LoggingMiddleware())



async def shutdown(dispatcher: Dispatcher):
	await dispatcher.storage.close()
	await dispatcher.storage.wait_closed()


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.create_task(other.auto_norm_klass(3))
	loop.create_task(other.send_food(5))
	loop.create_task(other.scheduled(5)) # поставим 10000 секунд, в качестве теста
	loop.create_task(other.anti_starosta(10))
	executor.start_polling(dp, skip_updates=True,on_shutdown=shutdown, on_startup=on_startup)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		loop.run_until_complete(loop.shutdown_asyncgens())
		loop.close()

	
	