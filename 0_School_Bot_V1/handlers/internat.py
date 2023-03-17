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
	internat = State()
	change_food = State()
	confirm = State()





async def ifinternat(message: types.Message):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		await message.answer('Вы отвечаете за интернат, вам нужно отправлять заявку о 6 разовом питании \n доступные команды можно узнать с помощью кнопок внизу', reply_markup= kb.internat_kb)
		await FSMAdmin.internat.set()
		return True
	else:
		return False

@dp.message_handler(commands=['Что_мне_делать?'],state=FSMAdmin.internat)
async def info_internat_command(message:types.Message):
	await message.answer('вам нужно отправлять заявку каждый день о питании интерната', reply_markup= kb.internat_kb)


@dp.message_handler(commands=['Команды_бота'],state=FSMAdmin.internat)
async def internat_commands_command(message:types.Message):
	await message.answer('на данный момент 4 команды: \n /Что_мне_делать?' + 
		'\n/Команды_бота' +
		'\n/Подать_заявку - отправить данные о питании' +
		'\n/Вопросы_и_Об_авторе - отправляет телеграмм для связи с разработчиком', reply_markup= kb.internat_kb)


@dp.message_handler(commands=['Подать_заявку_на_завтра'],state=FSMAdmin.internat)
async def get_food_internat_command(message:types.Message):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		day = tomorrow
		await message.answer(f'Завтрашний день: {day}')
		#if await sqlite_db.check_req_food_command(str(classofuser), day):
		#	await message.answer('Заявка на сегодня уже есть, проверь или удали её командой /Проверить_заявку')
		#	await state.finish()
		#	await FSMAdmin.internat.set()
		#else:
		read = await sqlite_db.read_internat_req_food_command(day)
		for ret in read:
			for x in range(6):
				d = {0: 'Завтрак 1', 1: 'Завтрак 2', 2:'Обед', 3: 'Полдник', 4: 'Ужин 1', 5: 'Ужин 2'}
				food = d[x]
				await message.answer(f'{food} - {ret[x]}', reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Изменить заявку {food}', callback_data=f'change {x}')))


@dp.message_handler(commands=['Корректировать_заявку'],state=FSMAdmin.internat)
async def get_food_internat_command(message:types.Message):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		day = datetime.date.today().isoformat()
		await message.answer(f'Сегодняшний день: {day}')
		#if await sqlite_db.check_req_food_command(str(classofuser), day):
		#	await message.answer('Заявка на сегодня уже есть, проверь или удали её командой /Проверить_заявку')
		#	await state.finish()
		#	await FSMAdmin.internat.set()
		#else:
		read = await sqlite_db.read_internat_req_food_command(day)
		for ret in read:
			for x in range(6):
				d = {0: 'Завтрак 1', 1: 'Завтрак 2', 2:'Обед', 3: 'Полдник', 4: 'Ужин 1', 5: 'Ужин 2'}
				food = d[x]
				await message.answer(f'{food} - {ret[x]}', reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Изменить заявку {food}', callback_data=f'change {x}')))
		
		#await FSMAdmin.confirm.set()

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('change'), state=FSMAdmin.internat)
async def del_callback_run(callback_query : types.CallbackQuery, state: FSMContext):
	truedata = callback_query.data.replace('change ', '')
	call_data = callback_query
	await change_internat(truedata, call_data, state)
	await callback_query.answer(text=f'Переход к редактированию заявки', show_alert=False)

async def change_internat(x, callback_query, state):
	d = {0: 'Завтрак 1', 1: 'Завтрак 2', 2:'Обед', 3: 'Полдник', 4: 'Ужин 1', 5: 'Ужин 2'}
	x = int(x)
	food = d[x]
	async with state.proxy() as data:
		data['food'] = x
	await bot.send_message(callback_query.from_user.id, f'Напишите сколько людей ест {food} целым числом')
	await FSMAdmin.change_food.set()

@dp.message_handler(state=FSMAdmin.change_food)
async def change_food_command(message:types.Message, state: FSMContext):
	d = {0: 'firstzavtrak', 1: 'secondzavtrak', 2:'obed', 3: 'poldnik', 4: 'firstuzhin', 5: 'seconduzhin'}
	g = {0: 'Завтрак 1', 1: 'Завтрак 2', 2:'Обед', 3: 'Полдник', 4: 'Ужин 1', 5: 'Ужин 2'}
	async with state.proxy() as data:
		try:
			async with state.proxy() as data:
				x = data['food']
				food = d[x]
				data['numberof'] = int(message.text)
				number = data['numberof']
				day = datetime.date.today().isoformat()

			await FSMAdmin.internat.set()
			await sqlite_db.internat_change_command(food, number, day)
			await message.answer(f'{g[x]} = {message.text}', reply_markup=kb.internat_kb)
		except:
			print(traceback.format_exc())
			await message.answer('Попробуйте написать одним числом без других букв (пример: 11)')



@dp.message_handler(commands= ['confirm', 'все_верно'], state=FSMAdmin.confirm)
async def confirm_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			await message.answer('Заявка отправлена, спасибо', reply_markup=kb.internat_kb)
			poln = data['poln']
			nepoln = data['nepoln']
			day = data['day']
			await sqlite_db.req_add_command(state)
			await bot.send_message(-821666496, f'{klass}: полных - {poln} неполных - {nepoln} \nдата: {day}')
			await state.finish()
			await FSMAdmin.normal.set()
		except:
			print(traceback.format_exc())
			await message.answer('Используй команду /Отправить_заявку заново для заполнения заявки', reply_markup = kb.internat_kb)


@dp.message_handler(commands=['Вопросы_и_Об_авторе'],state='*')
async def info_command(message:types.Message):
	await message.answer('По всем вопросам бота <a href="https://t.me/Kos_Tyanka">сюда</a>',parse_mode="HTML")

@dp.message_handler(commands=['give_starosta'],state=FSMAdmin.internat)
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
			

@dp.message_handler(state=FSMAdmin.internat)
async def empty_admin(message:types.Message):
	await message.answer('Вы отвечаете за интернат, вам нужно отправлять заявку о 6 разовом питании \n доступные команды можно узнать с помощью кнопок внизу', reply_markup= kb.internat_kb)




def register_handlers_internat(dp : Dispatcher):
	#dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(internat_commands_command, commands=['Что_мне_делать?'],state=FSMAdmin.internat)
	#dp.register_message_handler(empty,)
