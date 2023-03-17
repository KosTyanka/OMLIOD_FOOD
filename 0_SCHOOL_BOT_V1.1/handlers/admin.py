from aiogram import types, Dispatcher
from create_bot import dp, bot
from data_base import sqlite_db
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import keyboards as kb
import sqlite3
import datetime
import traceback    
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from handlers import client
from aiogram_calendar_Z import simple_cal_callback, SimpleCalendar, dialog_cal_callback

class FSMAdmin(StatesGroup):
	admin = State()

@dp.message_handler(commands=['id'],state='*')
async def get_chat_id_command(message: types.Message, state: FSMContext):
	await message.answer(message.chat.id)

@dp.message_handler(commands=['set'],state='*')
async def get_chat_id_command(message: types.Message, state: FSMContext):
	await message.answer(message.text)
	await state.finish()

async def ifadmin(message: types.Message):
	user_channel_status = await bot.get_chat_member(chat_id='-855152164', user_id=message.from_user.id)
	if user_channel_status["status"] != 'left':
		await message.answer('Вы админ бота, бот будет отправлять вам статистику автоматически \n доступные команды можно узнать с помощью кнопок внизу', reply_markup= kb.admin_kb)
		await FSMAdmin.admin.set()
		return True
	else:
		return False

@dp.message_handler(commands=['Что_мне_делать?'],state=FSMAdmin.admin)
async def info_command(message:types.Message):
	await message.answer('Бот будет отправлять заявки и статистику для вас, доступные команды можно узнать по кнопке внизу \n /команды бота', reply_markup= kb.admin_kb)


@dp.message_handler(commands=['Команды_бота'],state=FSMAdmin.admin)
async def admin_commands_command(message:types.Message):
	await message.answer('на данный момент 4 команды: \n /Что_мне_делать?' + 
		'\n/Команды_бота' +
		'\n/Получить_питание - отправляет данные о питании' +
		'\n/Вопросы_и_Об_авторе - отправляет телеграмм для связи с разработчиком', reply_markup= kb.admin_kb)


@dp.message_handler(commands=['Получить_питание', 'Календарь'],state=FSMAdmin.admin)
async def get_food_command(message:types.Message):
	await message.answer('Питание:', reply_markup = await SimpleCalendar().start_calendar())


# simple calendar usage
@dp.callback_query_handler(simple_cal_callback.filter(), state = FSMAdmin.admin)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
	selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
	day = date.strftime("%Y-%m-%d")
	read = await sqlite_db.sql_read_food_by_day(day)
	await callback_query.message.answer(f'Отправляю питание за {date.strftime("%d/%m/%Y")}')
	for ret in read:
		await callback_query.message.answer(f'класс: {ret[0].strip("[()]")} \nполных: {ret[1]} \nнеполных: {ret[2]} \nДата заявки: {ret[3]}')

	await callback_query.message.answer(f'Интернат за {date.strftime("%d/%m/%Y")}')
	read2 = await sqlite_db.read_internat_req_food_command(day)
	for ret in read2:
		await callback_query.message.answer(f'Питание интерната:\n' +
			f'Первый завтрак: {ret[0]}\n' +
			f'Второй завтрак: {ret[1]}\n' +
			f'Обед: {ret[2]}\n' +
			f'Полдник: {ret[3]}\n' +
			f'Первый ужин: {ret[4]}\n' +
			f'Второй ужин: {ret[5]}\n'
			)

	await callback_query.message.answer(f'Отсутствующие за {date.strftime("%d/%m/%Y")}')
	absent_data = await sqlite_db.get_all_absent_command(day)
	if absent_data:
		for ret in absent_data:
			await callback_query.message.answer(f'класс: {ret[0]}\n' +
				f'Отсутствующий: {ret[1]}\n' +
				f'Причина: {ret[3]}',)
	else:
		await callback_query.message.answer('нет отсутствующих')


	if selected:
		await callback_query.message.answer(
			f'Что дальше?',
			reply_markup= kb.after_calendar_admin_kb
		)

#DEPRECATED AND OBSOLETE
#ЭТО БУДЕТ CALLBACK QUERY
#@dp.message_handler(commands=['Получить_питание'],state=FSMAdmin.admin)
#async def get_food_callback(message:types.Message):
#	await message.answer('Высылаю питание:')
#	read = await sqlite_db.sql_read_food(message)
#	for ret in read:
#		await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nполных: {ret[1]} \nнеполных: {ret[2]} \nДата заявки: {ret[3]}')
#	await message.answer('Питание интерната:')
#	read = await sqlite_db.internat_read_food(message)
#	for ret in read:
#		if ret[1] != 0:
#			await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nинтернатников: {ret[1]} \nДата заявки: {ret[2]}')

@dp.message_handler(commands=['Вопросы_и_Об_авторе'],state='*')
async def info_command(message:types.Message):
	await message.answer('По всем вопросам бота <a href="https://t.me/Kos_Tyanka">сюда</a>',parse_mode="HTML")

@dp.message_handler(commands=['give_starosta'],state=FSMAdmin.admin)
async def give_starosta(message:types.Message):
	read = await sqlite_db.get_all_id()
	for ret in read:
		ret = ret[0]
		try:
			user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=ret)
			if user_channel_status["status"] != 'left':
				klass = (await sqlite_db.class_get_command(ret))[0]
				

				#klass = klass[0]
				user_id = ret
				phone_number = (await sqlite_db.sql_get_command(ret))[0]
				phone_number = phone_number[0]
				await sqlite_db.make_starosta(klass, user_id, phone_number)
		except:
			x = 1
			

@dp.message_handler(state=FSMAdmin.admin)
async def empty_admin(message:types.Message):
	await message.answer('Бот будет отправлять заявки и статистику для вас, доступные команды можно узнать по кнопке внизу \n /команды бота', reply_markup= kb.admin_kb)




def register_handlers_admin(dp : Dispatcher):
	#dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(info_command, commands=['Что_мне_делать?'],state=FSMAdmin.admin)
	#dp.register_message_handler(empty,)
