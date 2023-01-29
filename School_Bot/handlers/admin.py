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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers import client


class FSMAdmin(StatesGroup):
	admin = State()


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


@dp.message_handler(commands=['Получить_питание'],state=FSMAdmin.admin)
async def get_food_command(message:types.Message):
	await message.answer('Высылаю питание:')
	read = await sqlite_db.sql_read_food(message)
	for ret in read:
		await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nполных: {ret[1]} \nнеполных: {ret[2]} \nДата заявки: {ret[3]}')
	await message.answer('Питание интерната:')
	read = await sqlite_db.internat_read_food(message)
	for ret in read:
		if ret[1] != 0:
			await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nинтернатников: {ret[1]} \nДата заявки: {ret[2]}')

@dp.message_handler(commands=['Вопросы_и_Об_авторе'],state='*')
async def info_command(message:types.Message):
	await message.answer('По всем вопросам бота <a href="https://t.me/Kos_Tyanka">сюда</a>',parse_mode="HTML")

@dp.message_handler(state=FSMAdmin.admin)
async def empty_admin(message:types.Message):
	await message.answer('Бот будет отправлять заявки и статистику для вас, доступные команды можно узнать по кнопке внизу \n /команды бота', reply_markup= kb.admin_kb)

def register_handlers_admin(dp : Dispatcher):
	#dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(info_command, commands=['Что_мне_делать?'],state=FSMAdmin.admin)
	#dp.register_message_handler(empty,)
