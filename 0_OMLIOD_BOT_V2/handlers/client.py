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
from handlers import admin, internat
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class FSMAdmin(StatesGroup):
	phone = State()
	klass = State()
	normal = State()
	poln = State()
	nepoln = State()
	confirm = State()
	internat = State()
	absent = State()
	change_name = State()
	change_class = State()
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
	await message.reply('Отменил', reply_markup=kb.button_case_client)

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
	if message.text[0] == '/':
		async with state.proxy() as data:
			data['class'] = message.text[1:]
		await sqlite_db.sql_add_command(state)
		await state.finish()
		await FSMAdmin.normal.set()
		await message.answer(f'ваш класс {message.text[1:]}')
		await message.reply('Добро пожаловать в бота школы ОМЛИОД, используйте кнопки внизу для подробной информации', reply_markup=kb.button_case_client)
		await bot.forward_message(-821666496, message.chat.id, message.message_id)
	else:
		data['class'] = 0
		await sqlite_db.sql_add_command(state)
		await state.finish()
		await FSMAdmin.normal.set()
		await message.answer(f'Вы не ученик')
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


#@dp.callback_query_handler(lambda x: x.data and x.data.startswith('make'),state=FSMAdmin.normal)
#async def del_callback_run(callback_query: types.CallbackQuery, state: FSMContext):
#	async with state.proxy() as data:
#		data['class'] = callback_query.data.replace('make ', '')
#		await FSMAdmin.internat.set()
#		await callback_query.answer(text=f'{callback_query.data.replace("make ", "")} начните писать количество интерната', show_alert=False)
#		await bot.send_message(callback_query.from_user.id, f'{callback_query.data.replace("make ", "")} начните писать количество интерната', reply_markup=types.ReplyKeyboardRemove())

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

@dp.message_handler(commands=['Отправить_заявку'],state='*')
async def make_request_command_new(message:types.Message, state: FSMContext):
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=message.from_user.id)
	if user_channel_status["status"] != 'left':
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		classofuser = classofuser[0]
		day = datetime.date.today().isoformat()
		#print(str(classofuser))
		if await sqlite_db.check_req_food_command(str(classofuser), day):
			await message.answer('Заявка на сегодня уже есть, проверь или удали её командой /Проверить_заявку')
			await state.finish()
			await FSMAdmin.normal.set()
		else:
			assign_talon = InlineKeyboardMarkup(row_width=3)
			read = await sqlite_db.get_classmates(classofuser)
			await message.answer(f'твой класс: {classofuser}')
			for profile_data in read:
				if profile_data[4] == '0' or profile_data[4] == 0:
					talon = "Талона нет"
				elif profile_data[5] == 1:
					talon = f"Ученик пообедал: {profile_data[4]}"
				else:
					talon = profile_data[4]
				poln_button = InlineKeyboardButton(text="полный", callback_data=f'assign_talon|{"Полный"}|{profile_data[1]}')
				nepoln_button = InlineKeyboardButton(text="неполный", callback_data=f'assign_talon|{"Неполный"}|{profile_data[1]}')
				no_button = InlineKeyboardButton(text="не ест", callback_data=f'assign_talon|{0}|{profile_data[1]}')
				assign_talon.add(poln_button, nepoln_button, no_button)
				await message.answer(f'Ученик: {profile_data[1]}\n' +
					f'Талон: {talon}', reply_markup= assign_talon)
			poln_num = 0
			nepoln_num = 0
			for profile_data in read:
				if profile_data[4] == 'Полный':
					poln_num += 1
				elif profile_data[4] == 'Неполный':
					nepoln_num += 1
			confirm_keyboard = InlineKeyboardMarkup(row_width=2)
			confirm_button = InlineKeyboardButton(text="Подтвердить", callback_data=f'final_request|{poln_num}|{nepoln_num}|{classofuser}')
			cancel_button = InlineKeyboardButton(text="Отменить", callback_data=f'cancel_request')
			manual_request_button = InlineKeyboardButton(text="Ввести вручную", callback_data=f'manual_request')
			confirm_keyboard.add(confirm_button, cancel_button).add(manual_request_button)
			msg = await message.answer(f'Заявка на сегодня: Полных - {poln_num}, Неполных - {nepoln_num}',reply_markup=confirm_keyboard)
			await state.update_data(msg_id=msg.message_id)
	else:
		await bot.send_message(message.from_user.id, 'У тебя нет прав для отправки заявки, напиши сюда для получения доступа @Kos_Tyanka')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('final_request'), state='*')
async def final_request_callback(callback_query : types.CallbackQuery, state: FSMContext):
	data = callback_query.data.split('|')
	poln_num = data[1]
	nepoln_num = data[2]
	classofuser = data[3]
	day = datetime.date.today().isoformat()
	await bot.send_message(-821666496, f'класс {classofuser}: полных - {poln_num} неполных - {nepoln_num} \nдата: {day}')
	await bot.send_message(-855152164, f'класс {classofuser}: полных - {poln_num} неполных - {nepoln_num} \nдата: {day}')
	await sqlite_db.req_add_new_command(classofuser, poln_num, nepoln_num, day)
	await callback_query.message.answer(f'Заявка отправлена, спасибо\nЗаявка: полных - {poln_num}, неполных - {nepoln_num}')
	await state.finish()

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('cancel_request'), state='*')
async def cancel_request_callback(callback_query : types.CallbackQuery, state: FSMContext):
	await callback_query.message.delete()
	await callback_query.message.answer(f'Отменил',reply_markup=kb.button_case_client)
	await state.finish()

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('manual_request'), state='*')
async def manual_request_callback(callback_query : types.CallbackQuery, state: FSMContext):
	classofuser = await sqlite_db.class_get_command(callback_query.from_user.id)
	classofuser = classofuser[0]
	day = datetime.date.today().isoformat()
	#print(str(classofuser))
	if await sqlite_db.check_req_food_command(str(classofuser), day):
		await callback_query.message.answer('Заявка на сегодня уже есть, проверь или удали её командой /Проверить_заявку')
		await state.finish()
		await FSMAdmin.normal.set()
	else:
		#classofuser = await sqlite_db.class_get_command(message.from_user.id)
		#await message.answer(classofuser)
		async with state.proxy() as data:
			data['class'] = str(classofuser)
		await FSMAdmin.poln.set()
		await callback_query.message.answer('Напиши сколько полных одним числом или /отмена для отмены заявки', reply_markup=types.ReplyKeyboardRemove())

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('assign_talon'), state='*')
async def assign_talon_callback(callback_query : types.CallbackQuery, state: FSMContext):
	callback_data = callback_query.data.split('|')
	talon = callback_data[1]
	await sqlite_db.update_talon(talon,callback_data[2])
	assign_talon = InlineKeyboardMarkup(row_width=3)
	poln_button = InlineKeyboardButton(text="полный", callback_data=f'assign_talon|{"Полный"}|{callback_data[2]}')
	nepoln_button = InlineKeyboardButton(text="неполный", callback_data=f'assign_talon|{"Неполный"}|{callback_data[2]}')
	no_button = InlineKeyboardButton(text="не ест", callback_data=f'assign_talon|{0}|{callback_data[2]}')
	assign_talon.add(poln_button, nepoln_button, no_button)
	profile_data = await sqlite_db.get_profile_by_name(callback_data[2])
	if profile_data[4] == '0' or profile_data[4] == 0:
		talon = "Талона нет"
	elif profile_data[5] == 1:
		talon = f"Ученик пообедал: {profile_data[4]}"
	else:
		talon = profile_data[4]
	
	try:
		await callback_query.message.edit_text(f'Ученик: {callback_data[2]}\n' +
						f'Талон: {talon}', reply_markup= assign_talon)
	except:
		await callback_query.answer(f'талон {talon} уже присвоен для ученика {callback_data[2]}', show_alert=True)
		donothing =0
	await bot.answer_callback_query(callback_query.id)
	msg_id = (await state.get_data())['msg_id']
	classofuser = await sqlite_db.class_get_command(callback_query.from_user.id)
	classofuser = classofuser[0]
	poln_num = 0
	nepoln_num = 0
	confirm_keyboard = InlineKeyboardMarkup(row_width=2)
	confirm_button = InlineKeyboardButton(text="Подтвердить", callback_data=f'final_request|{poln_num}|{nepoln_num}|{classofuser}')
	cancel_button = InlineKeyboardButton(text="Отменить", callback_data=f'cancel_request')
	manual_request_button = InlineKeyboardButton(text="Ввести вручную", callback_data=f'manual_request')
	confirm_keyboard.add(confirm_button, cancel_button).add(manual_request_button)
	read = await sqlite_db.get_classmates(classofuser)
	for profile_data in read:
	    if profile_data[4] == 'Полный':
	        poln_num += 1
	    elif profile_data[4] == 'Неполный':
	        nepoln_num += 1

	await bot.edit_message_text(f'Заявка на сегодня: Полных - {poln_num}, Неполных - {nepoln_num}', chat_id=callback_query.message.chat.id, message_id=msg_id,reply_markup= confirm_keyboard)



@dp.message_handler(commands=['Отправить_заявку'],state='*')
async def make_request_command(message:types.Message, state: FSMContext):
	internat_channel_status = await bot.get_chat_member(chat_id='-837114163', user_id=message.from_user.id)
	if internat_channel_status["status"] != 'left':
		await bot.send_message(message.from_user.id, f'Напишите еще одно сообщение')
		await internat.ifinternat(message)
		print('заведующий интерната зашел')	
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=message.from_user.id)
	if user_channel_status["status"] != 'left':
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		classofuser = classofuser[0]
		day = datetime.date.today().isoformat()
		#print(str(classofuser))
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
	classofuser = await sqlite_db.class_get_command(message.from_user.id)
	day = datetime.date.today().isoformat()
	await message.answer(f'ваш класс: {str(classofuser[0])}')
	await message.answer(f'сегодняшний день: {day}')
	food_data = await sqlite_db.get_req_food_command(str(classofuser[0]), day)
	#await message.answer(food_data)
	if food_data != None:
		a = food_data[0]
		b = food_data[1]
		await message.answer(f'Заявка на сегодня: полных - {a}, неполных - {b}', reply_markup=kb.food_kb)
	else:
		await message.answer('Не нашел заявку на сегодня')

	absent_data = await sqlite_db.get_absent_command(classofuser[0],day)
	if absent_data:
		for ret in absent_data:
			await message.answer(f'Отсутствующий: {ret[1]}\n' +
				f'Причина: {ret[3]}', reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'whomissingdel{ret[1]}|{day}')))
	else:
		await message.answer('сегодня нет отсутствующих')

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('whomissingdel'), state=FSMAdmin.normal)
async def absent_del_callback_run(callback_query : types.CallbackQuery):
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=callback_query.from_user.id)
	if user_channel_status["status"] != 'left':
		user_id = callback_query.from_user.id

		data = callback_query.data.replace('whomissingdel', '').split('|')
		whomissing = data[0]
		day = data[1]
		await sqlite_db.absent_delete_command(whomissing, day)
		await callback_query.answer(text=f'{whomissing} удален', show_alert=True)
		await bot.send_message(callback_query.from_user.id, f'Что дальше?', reply_markup=kb.button_case_client)
	else:
   		await bot.send_message(callback_query.from_user.id, 'У тебя нет прав для удаления заявки, напиши сюда для получения доступа @Kos_Tyanka')
   		await callback_query.answer(text=f'Прочитай сообщение', show_alert=False)

@dp.message_handler(commands=['Мой_талон'], state = FSMAdmin.normal)
async def show_talon_command(message:types.Message):
	profile_exists = await sqlite_db.check_profile_exists(message.from_user.id)
	if not profile_exists:
		await message.answer('Используй команду /профиль для создания профиля')
	else:
		W, H = (300, 300)
	
		imgPIL = Image.open('TALON.png')
		font = ImageFont.truetype("arial.ttf", size=35)
		fontname = ImageFont.truetype("arial.ttf", size=25)
		idraw = ImageDraw.Draw(imgPIL)
		profile_data = await sqlite_db.get_profile(message.from_user.id)
		talon = profile_data[4]
		w, h = idraw.textsize(talon, font = font)
		if talon != 0 and talon != '0':
			idraw.text(((W-w)/2, 60), f'{talon}', font=font, fill=(0, 0, 0))
		else:
			idraw.text((65, 60), f'Талона нет', font=font, fill=(0, 0, 0))
	
		#if profile_data[5]:
		#	idraw.text((95, 95), f'Поел', font=font, fill=(0,0,0))
		#else:
		#	idraw.text((95, 95), f'Не ел', font=font, fill=(0,0,0))
	
	
		if ' ' in profile_data[1]:
			surname, name = profile_data[1].split(' ')
			w, h = idraw.textsize(surname, font = font)
			idraw.text(((W-w)/2, 125), f'{surname}', font=font, fill=(0,0,0))
			w, h = idraw.textsize(name, font = font)
			idraw.text(((W-w)/2, 175), f'{name}', font=font, fill=(0,0,0))
		else:
			idraw.text((30, 105), f'{profile_data[1]}', font=fontname, fill=(0,0,0))
		day = datetime.date.today().isoformat()
		w, h = idraw.textsize(day, font= font)
		idraw.text(((W-w)/2, 230), f'{day}', font=font, fill=(0,0,0))
		# Save the modified image to a BytesIO buffer
		img_buffer = BytesIO()
		imgPIL.save(img_buffer, format='PNG')
		img_buffer.seek(0)
	
		# Pass the bytes from the buffer to the bot.send_photo methodd
		await bot.send_photo(chat_id=message.chat.id, photo=img_buffer)
	
		if profile_data[5] == 1:
			await message.answer(f"Вы сегодня поели {profile_data[4]}")


@dp.message_handler(commands=['Профиль'], state = FSMAdmin.normal)
async def profile_command(message:types.Message):
	classofuser = await sqlite_db.class_get_command(message.from_user.id)
	classofuser = classofuser[0]
	#Nameofuser = await sqlite_db.get_name(message.from_user.id)
	#Nameofuser = Nameofuser[0]
	phone_number = await sqlite_db.get_phone_number(message.from_user.id)
	phone_number = phone_number[0]
	profile_exists = await sqlite_db.check_profile_exists(message.from_user.id)
	#Проверка существования аккаунта
	if profile_exists:
		donothing = 0
	else:
		await sqlite_db.make_profile_command(classofuser, 'Нет данных', message.from_user.id, phone_number, 0, 0)
		await message.answer('Используй кнопку чтобы поменять имя')
	#конец проверки
	profile_data = await sqlite_db.get_profile(message.from_user.id)
	profile = InlineKeyboardMarkup(row_width=2)
	change_profile_name_button = InlineKeyboardButton(text="Поменять имя", callback_data=f'change_name|{message.from_user.id}')
	get_myfood_button = InlineKeyboardButton(text="Получить выписку за месяц", callback_data=f'get_myfood|{message.from_user.id}')
	#change_profile_class = InlineKeyboardButton(text="Поменять класс", callback_data=f'change_class|{message.from_user.id}')
	profile.add(change_profile_name_button, get_myfood_button)
	if profile_data[4] == '0' or profile_data[4] == 0:
		talon = "Талона нет"
	elif profile_data[5] == 1:
		talon = f"Вы сегодня поели {profile_data[4]}"
	else:
		talon = profile_data[4]

	await message.answer(f'Ваш профиль:\nкласс: {profile_data[0]}\n' +
		f'номер: {profile_data[3]}\n' +
		f'Фамилия, имя: {profile_data[1]}\n' +
		f'Талон: {talon}\n', reply_markup=profile
		)

	if profile_data[1] == 'Нет данных':
		await message.answer('Используй кнопку чтобы изменить имя')

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('change_name'), state=FSMAdmin.normal)
async def change_name_callback_run(callback_query: types.CallbackQuery):
	user_id = callback_query.data.split('|')[1]
	#print(user_id)
	await FSMAdmin.change_name.set()
	await bot.send_message(callback_query.from_user.id, f'Напиши свою фамилию и имя одним сообщением (пример: "Аубакиров Жаслан"')

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('get_myfood'), state=FSMAdmin.normal)
async def change_name_callback_run(callback_query: types.CallbackQuery):
	user_id = callback_query.data.split('|')[1]
	#print(user_id)
	Nameofuser = await sqlite_db.get_name(user_id)
	Nameofuser= Nameofuser[0]
	classofuser = await sqlite_db.class_get_command(user_id)
	classofuser = classofuser[0]
	day = datetime.date.today().isoformat()
	month = day[0:7]
	myfood = await sqlite_db.get_myfood_command(classofuser, Nameofuser, month)
	#print(myfood)
	poln_num = 0
	nepoln_num = 0
	if myfood and myfood != None:
		for x in myfood:
			if x[2] == 'Полный':
				poln_num += 1
			elif x[2] == 'Неполный':
				nepoln_num += 1

	myfood_getinfo = InlineKeyboardMarkup(row_width=1)
	myfood_getinfo_button = InlineKeyboardButton(text='Подробнее', callback_data=f'myfood_getinfo|{callback_query.from_user.id}')
	myfood_getinfo.add(myfood_getinfo_button)
	await bot.send_message(callback_query.from_user.id, f'Ваша выписка за месяц: Полных - {poln_num}, Неполных - {nepoln_num}', reply_markup= myfood_getinfo)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('myfood_getinfo'), state=FSMAdmin.normal)
async def change_name_callback_run(callback_query: types.CallbackQuery):
	user_id = callback_query.data.split('|')[1]
	#print(user_id)
	Nameofuser = await sqlite_db.get_name(user_id)
	Nameofuser= Nameofuser[0]
	classofuser = await sqlite_db.class_get_command(user_id)
	classofuser = classofuser[0]
	day = datetime.date.today().isoformat()
	month = day[0:7]
	myfood_all = await sqlite_db.get_myfood_command(classofuser, Nameofuser, month)
	myfood_data = 'Полная выписка:'
	if myfood_all and myfood_all != None:
		for x in myfood_all:
			myfood_data += f'\nДень: {x[3]}, Поел: {x[2]}'
	else:
		await(bot.send_message(callback_query.from_user.id, f'Выписка пуста'))
	await bot.send_message(callback_query.from_user.id, f'{myfood_data}')

@dp.message_handler(state = FSMAdmin.change_name)
async def change_name_message(message:types.Message):
	try:
		await sqlite_db.change_name_command(message.text, message.from_user.id)
		await sqlite_db.update_name_in_food(message.text, message.from_user.id)
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		classofuser = classofuser[0]
		#Проверка существования аккаунта
		Nameofuser = await sqlite_db.get_name(message.from_user.id)
		Nameofuser= Nameofuser[0]
		phone_number = await sqlite_db.get_phone_number(message.from_user.id)
		phone_number = phone_number[0]
		profile = InlineKeyboardMarkup(row_width=2)
		change_profile_name = InlineKeyboardButton(text="Поменять имя", callback_data=f'change_name|{message.from_user.id}')
		#change_profile_class = InlineKeyboardButton(text="Поменять класс", callback_data=f'change_class|{message.from_user.id}')
		profile.add(change_profile_name)
		await message.answer(f'Ваш профиль:\nкласс: {classofuser}\n' +
		f'номер: {phone_number}\n' +
		f'Фамилия, имя: {Nameofuser}', reply_markup=profile
		)
		await message.answer('Успешно внес изменения', reply_markup=kb.button_case_client)
		await FSMAdmin.normal.set()
	except:
		print(traceback.format_exc())
		await message.answer('Произошла ошибка, если есть вопросы напиши сюда @Kos_Tyanka')
		await FSMAdmin.normal.set()




@dp.message_handler(commands=['Добавить_Отсутствующего'],state=FSMAdmin.normal)
async def make_absent_command(message:types.Message, state: FSMContext):
	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=message.from_user.id)
	if user_channel_status["status"] != 'left':
		classofuser = await sqlite_db.class_get_command(message.from_user.id)
		classofuser = classofuser[0]
		async with state.proxy() as data:
				data['class'] = str(classofuser)
		await FSMAdmin.absent.set()
		await bot.send_message(message.from_user.id, f'Напиши Фамилию, Имя отсутствующего. Ваш класс: {classofuser}')
	else:
		await bot.send_message(message.from_user.id, 'У тебя нет прав для отправки списка отсутствующих, напиши сюда для получения доступа @Kos_Tyanka')

@dp.message_handler(state= FSMAdmin.absent)
async def make_absent_command(message:types.Message, state: FSMContext):
	async with state.proxy() as data:
		try:
			#Должен ответить Текстом отсутствующего
			async with state.proxy() as data:
				data['AbName'] = str(message.text)
			#await FSMAdmin.confirm.set()
			absent_confirm = InlineKeyboardMarkup(row_width=2)
			zabolel_button = InlineKeyboardButton(text="Болезнь", callback_data=f'absent|{1}|{data["AbName"]}')
			petition_button = InlineKeyboardButton(text="Заявление", callback_data=f'absent|{2}|{data["AbName"]}')
			prikaz_button = InlineKeyboardButton(text="Приказ", callback_data=f'absent|{3}|{data["AbName"]}')
			another_button = InlineKeyboardButton(text="Другое", callback_data=f'absent|{4}|{data["AbName"]}')
			cancel_button = InlineKeyboardButton(text="Отмена", callback_data=f'absent|{5}|{data["AbName"]}')
			absent_confirm.add(zabolel_button, petition_button, prikaz_button, another_button).add(cancel_button)
			await message.answer(f'Отсутствующий: {data["AbName"]}', reply_markup=absent_confirm)
			await state.finish()
			await FSMAdmin.normal.set()
		except:
			await message.answer(f'Произошла ошибка, напиши сюда @Kos_Tyanka')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('absent'), state=FSMAdmin.normal)
async def del_callback_run(callback_query: types.CallbackQuery):
	d = {1: 'Болезнь', 2: 'Заявление', 3: 'Приказ', 4: 'Другое', 5: 'Отмена'}
	data = callback_query.data.split('|')
	#whyabsentdata = data[1]
	whyabsent = d[int(data[1])]
	whoabsent = data[2]
	classofuser = await sqlite_db.class_get_command(callback_query.from_user.id)
	classofuser = str(classofuser[0])
	#class TEXT, whomissing TEXT, day DATE, why TEXT
	day = datetime.date.today().isoformat()
	if int(data[1]) != 5:
		await sqlite_db.absent_add_command(classofuser, whoabsent, day, whyabsent)
		await callback_query.answer(text=f'{whoabsent} занесен в базу по причине {whyabsent}.', show_alert=False)
		await bot.send_message(callback_query.from_user.id, f'{whoabsent} отсутствует по причине {whyabsent}')
		await bot.send_message(-855152164, f'класс: {classofuser}\n{whoabsent} отсутствует по причине {whyabsent}')
	else:
		await callback_query.answer('Отменил')
	await bot.send_message(callback_query.from_user.id, f'Проверить или удалить отсутствующих можно командой /Проверить_заявку', reply_markup=kb.button_case_client)
	await bot.delete_message(callback_query.from_user.id, message_id =callback_query.message.message_id)

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
		await sqlite_db.food_delete_command(str(classofuser[0]), day)
		await callback_query.answer(text=f'Заявка удалена.', show_alert=True)
		await bot.send_message(callback_query.from_user.id, f'Что дальше?', reply_markup=kb.button_case_client)
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
			
			klass = data['class']
			klass = klass.strip("[('',)]")
			#print(klass)
			poln = data['poln']
			nepoln = data['nepoln']
			day = data['day']
			await bot.send_message(-821666496, f'класс {klass}: полных - {poln} неполных - {nepoln} \nдата: {day}')
			await bot.send_message(-855152164, f'класс {klass}: полных - {poln} неполных - {nepoln} \nдата: {day}')
			await sqlite_db.req_add_new_command(klass, poln, nepoln, day)
			await state.finish()
			await FSMAdmin.normal.set()
			await message.answer('Заявка отправлена, спасибо', reply_markup=kb.button_case_client)
		except:
			print(traceback.format_exc())
			await message.answer('Произошла ошибка, Используй команду /Отправить_заявку заново для заполнения заявки', reply_markup=kb.button_case_client)
			


#@dp.message_handler(commands=['Отправить_заявку'],state='*')
#async def make_request_command(message:types.Message, state: FSMContext):
#	user_channel_status = await bot.get_chat_member(chat_id='-1001870898709', user_id=message.from_user.id)
#	if user_channel_status["status"] != 'left':
#		classofuser = await sqlite_db.class_get_command(message.from_user.id)
#		day = datetime.date.today().isoformat()
#		#classofuser = await sqlite_db.class_get_command(message.from_user.id)
#		#await message.answer(classofuser)
#		async with state.proxy() as data:
#			data['class'] = str(classofuser)
#		await FSMAdmin.poln.set()
#		await message.answer('Напиши сколько полных одним числом или /отмена для отмены заявки', reply_markup=types.ReplyKeyboardRemove())
#	else:
#		await bot.send_message(message.from_user.id, 'У тебя нет прав для отправки заявки, напиши сюда для получения доступа @Kos_Tyanka')



@dp.message_handler(commands = 'class', state=FSMAdmin.normal)
async def change_klass(message : types.Message, state= FSMAdmin.normal):
	klass = message.text.replace('/class ', '')
	await sqlite_db.change_klass(klass, message.from_user.id)
	await sqlite_db.change_klass_profile(klass, message.from_user.id)
	await message.answer("Сменил класс", reply_markup = kb.button_case_client)

@dp.message_handler(state=FSMAdmin.normal)
async def empty_normal(message : types.Message, state= FSMAdmin.normal):
	if await admin.ifadmin(message):
		print('админ зашел')
	elif await internat.ifinternat(message):
		print('заведующий интерната зашел')
	else:
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
	elif await internat.ifinternat(message):
		print('заведующий интерната зашел')
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
	elif await internat.ifinternat(message):
		print('заведующий интерната зашел')
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