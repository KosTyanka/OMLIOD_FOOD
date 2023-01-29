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
from handlers import admin

class FSMAdmin(StatesGroup):
	phone = State()
	klass = State()
	normal = State()
	poln = State()
	nepoln = State()
	confirm = State()
	internat = State()
	#admin = State()
	#nick = State()

@dp.message_handler(commands=['id'],state='*')
async def get_chat_id_command(message: types.Message, state: FSMContext):
	await message.answer(message.chat.id)


@dp.message_handler(state='*', commands=['отмена', 'cancel'])
#@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_state_handler(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.reply('Отменил, чтобы продолжить пользоваться ботом напиши любое сообщение')

@dp.message_handler(content_types=['contact'], state=FSMAdmin.phone)
async def process_start_command(message: types.Message, state: FSMContext):

	async with state.proxy() as data:
		data['phone'] = message.contact.phone_number
	async with state.proxy() as data:
		data['userid'] = message.from_user.id
	async with state.proxy() as data:
		data['nick'] = message.from_user.username
	#	data['class'] = 0
	#await sqlite_db.sql_add_command(state)
	#await state.finish()
	await message.reply("внес номер телефона в базу")
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		async with state.proxy() as data:
			data['class'] = 0
		await sqlite_db.sql_add_command(state)
		await FSMAdmin.normal.set()
		await message.answer('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
	else:
		await FSMAdmin.klass.set()
		await message.answer('Выбери свой класс', reply_markup = kb.class_select_buttons)

@dp.message_handler(state=FSMAdmin.klass)
async def select_class_command(message: types.Message, state: FSMContext):

	async with state.proxy() as data:
		data['class'] = message.text[1:]
	await sqlite_db.sql_add_command(state)
	await state.finish()
	await FSMAdmin.normal.set()
	await message.answer(f'ваш класс {message.text[1:]}')
	await message.reply('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
	await bot.forward_message(-821666496, message.chat.id, message.message_id)
	


#@dp.message_handler(commands=['start'])
#async def process_start_command(message: types.Message):
#    await message.reply("Привет!\nНапиши мне что-нибудь!")

@dp.message_handler(commands=['Вопросы_и_Об_авторе'],state='*')
async def info_command(message:types.Message):
	await message.answer('По всем вопросам бота <a href="https://t.me/Kos_Tyanka">сюда</a>',parse_mode="HTML")
	

@dp.message_handler(commands=['Доступные_команды'],state=FSMAdmin.normal)
async def whatican_command(message:types.Message):
	await message.answer('На данный момент доступны \n /Вопросы_и_Об_авторе \n /Доступные_команды \n /Проверить_заявку ')
	await message.answer('Для старост: используйте команду  /Отправить_заявку для отправки заявки на питание')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('make'),state=FSMAdmin.normal)
async def del_callback_run(callback_query: types.CallbackQuery, state: FSMContext):
	async with state.proxy() as data:
		data['class'] = callback_query.data.replace('make ', '')
		await FSMAdmin.internat.set()
		await callback_query.answer(text=f'{callback_query.data.replace("make ", "")} начните писать количество интерната', show_alert=False)
		await bot.send_message(callback_query.from_user.id, f'{callback_query.data.replace("make ", "")} начните писать количество интерната', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=FSMAdmin.internat)
async def make_internat_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			async with state.proxy() as data:
				data['internat'] = int(message.text)
				day = datetime.date.today().isoformat()
				data['day'] = day
			await sqlite_db.internat_update_command(state)
			await message.answer(f'Подтвердите правильность заявки класс: {data["class"]} интернатников: {data["internat"]}')
			await message.answer('Если что-то не так: отправьте заявку еще раз с помощью команды /отправить_заявку', reply_markup=kb.button_case_client)
			await state.finish()
			await FSMAdmin.normal.set()
		except:
			print(traceback.format_exc())
			await message.answer('Попробуй написать одним числом без других букв (пример: 11)')

			

@dp.message_handler(commands=['Отправить_заявку'],state=FSMAdmin.normal)
async def make_request_command(message:types.Message, state: FSMContext):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		day = datetime.date.today().isoformat()
		read = await sqlite_db.internat_read_food(message)
		for ret in read:
			await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nинтернатников: {ret[1]} \nДата заявки: {ret[2]}', reply_markup=kb.button_case_client)
			await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
				add(InlineKeyboardButton(f'Добавить заявку {ret[0]}', callback_data=f'make {ret[0]}')))
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=message.from_user.id)
	if user_channel_status["status"] != 'left':
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		day = datetime.date.today().isoformat()
		if await sqlite_db.check_req_food_command(str(classofuser), day):
			await message.answer('Заявка на сегодня уже есть, проверь или удали её командой /Проверить_заявку')
			await state.finish()
			await FSMAdmin.normal.set()
		else:
			#classofuser = await sqlite_db.class_get_command(message.from_user.id)
			#await message.answer(classofuser)
			async with state.proxy() as data:
				data['class'] = str(classofuser)
			await FSMAdmin.poln.set()
			await message.answer('Напиши сколько полных одним числом или /отмена для отмены заявки', reply_markup=types.ReplyKeyboardRemove())
	else:
		await bot.send_message(message.from_user.id, 'У тебя нет прав для отправки заявки, напиши сюда для получения доступа @Kos_Tyanka')
	
@dp.message_handler(commands=['Проверить_заявку'],state=FSMAdmin.normal)
async def check_request_command(message:types.Message, state: FSMContext):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		day = datetime.date.today().isoformat()
		read = await sqlite_db.internat_read_food(message)
		for ret in read:
			await bot.send_message(message.from_user.id, f'класс: {ret[0].strip("[()]")} \nинтернатников: {ret[1]} \nДата заявки: {ret[2]}', reply_markup=kb.button_case_client)
			await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
				add(InlineKeyboardButton(f'Добавить заявку {ret[0]}', callback_data=f'make {ret[0]}')))
	else:
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		day = datetime.date.today().isoformat()
		await message.answer(f'ваш класс: {str(classofuser[0])}')
		await message.answer(f'сегодняшний день: {day}')
		food_data = await sqlite_db.get_req_food_command(str(classofuser), day)
		#await message.answer(food_data)
	
	if food_data != None:
		a = food_data[0]
		b = food_data[1]
		await message.answer(f'Заявка на сегодня: полных - {a}, неполных - {b}', reply_markup=kb.food_kb)
	else:
		await message.answer('Не нашел заявку на сегодня')


#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del'))
#@bot.callback_query_handler(func=lambda c: c.data == 'callback')
#async def del_callback_run(callback_query: types.CallbackQuery):
#    print(callback_query.data.replace('del ', ''))
#    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)

@dp.callback_query_handler(text = 'delete', state=FSMAdmin.normal)
async def del_callback_run(callback_query : types.CallbackQuery):
	#await callback_query.message.answer('нажата')
	#print(callback_query.data)
	#print("da")
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=callback_query.from_user.id)
	if user_channel_status["status"] != 'left':
		user_id = callback_query.from_user.id
		classofuser = await sqlite_db.class_get_command(user_id)
		day = datetime.date.today().isoformat()
		await sqlite_db.food_delete_command(str(classofuser), day)
		await callback_query.answer(text=f'Заявка удалена.', show_alert=True)
	else:
   		await bot.send_message(callback_query.from_user.id, 'У тебя нет прав для удаления заявки, напиши сюда для получения доступа @Kos_Tyanka')
   		await callback_query.answer(text=f'Прочитай сообщение', show_alert=False)


@dp.message_handler(state=FSMAdmin.poln)
async def make_request_poln_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			async with state.proxy() as data:
				data['poln'] = int(message.text)
			await FSMAdmin.nepoln.set()
			await message.answer('Теперь напиши кол-во неполных или /отмена для отмены заявки')
		except:
			print(traceback.format_exc())
			await message.answer('Попробуй написать одним числом без других букв (пример: 11)')
			

@dp.message_handler(state=FSMAdmin.nepoln)
async def make_request_nepoln_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			async with state.proxy() as data:
				data['nepoln'] = int(message.text)
				data['day'] = datetime.date.today().isoformat()
			await FSMAdmin.confirm.set()
			await message.answer(f'Подтверди правильность заявки: полных - {data["poln"]}, неполных - {data["nepoln"]} ', reply_markup=kb.buttons_confirm)
		except:
			print(traceback.format_exc())
			await message.answer('Попробуй написать одним числом без других букв (пример: 12)')
		

@dp.message_handler(commands= ['confirm', 'все_верно'], state=FSMAdmin.confirm)
async def confirm_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			await sqlite_db.req_add_command(state)
			await message.answer('Заявка отправлена, спасибо', reply_markup=kb.button_case_client)
			await state.finish()
			await FSMAdmin.normal.set()
		except:
			await message.answer('Используй команду /Отправить_заявку заново для заполнения заявки')
			

@dp.message_handler(state=FSMAdmin.confirm)
async def confirm_empty_command(message:types.Message):
	await message.answer('Используй кнопки внизу или напиши /confirm для подтверждения или /cancel для отмены')

@dp.message_handler(commands = 'class', state=FSMAdmin.normal)
async def change_klass(message : types.Message, state= FSMAdmin.normal):
	klass = message.text.replace('/class ', '')
	await sqlite_db.change_klass(klass, message.from_user.id)
	await message.answer("Сменил класс", reply_markup = kb.button_case_client)

@dp.message_handler(state=FSMAdmin.normal)
async def empty_normal(message : types.Message, state= FSMAdmin.normal):
	if await admin.ifadmin(message):
		print('админ зашел')
	await message.reply('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
	await bot.forward_message(-821666496, message.chat.id, message.message_id)


@dp.message_handler(state= FSMAdmin.phone)
async def empty_reg(message : types.Message, state= None):
	if not await sqlite_db.user_exists(message.from_user.id):
		await message.answer('Вы не зарегистрированы, пожалуйста предоставьте свой номер телефона', reply_markup=kb.reg_kb)
	#elif ID ЗАВУЧА/КОГО ТО ВАЖНОГО: ДАТЬ АДМИНКУ
	#efif ID ВОЗМОЖНО СТАРОСТ
	elif await admin.ifadmin(message):
		print('админ зашел')
	else:
		await FSMAdmin.normal.set()
		await message.reply('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
		await bot.forward_message(-821666496, message.chat.id, message.message_id)


async def empty(message : types.Message, state= None):
	if not await sqlite_db.user_exists(message.from_user.id):
		await message.answer('Вы не зарегистрированы, пожалуйста предоставьте свой номер телефона', reply_markup=kb.reg_kb)
		await FSMAdmin.phone.set()
	#elif ID ЗАВУЧА/КОГО ТО ВАЖНОГО: ДАТЬ АДМИНКУ
	#efif ID ВОЗМОЖНО СТАРОСТ
	elif await admin.ifadmin(message):
		print('админ зашел')
	else:
		await FSMAdmin.normal.set()
		await message.reply('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
		await bot.forward_message(-821666496, message.chat.id, message.message_id)


#async def ifadmin(message: types.Message):
#	user_channel_status = await bot.get_chat_member(chat_id='-855152164', user_id=message.from_user.id)
#	if user_channel_status["status"] != 'left':
#		await message.answer('Вы админ бота, бот будет отправлять вам статистику автоматически \n доступные команды можно узнать с помощью кнопок внизу', reply_markup= kb.admin_kb)
#		await FSMAdmin.admin.set()
#		return True
#	else:
#		return False




def register_handlers_client(dp : Dispatcher):
	#dp.register_message_handler(process_start_command, commands=['start'])
    #dp.register_message_handler(process_help_command, commands=['help', 'Доступные_команды'])
	dp.register_message_handler(empty,)