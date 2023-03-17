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
import asyncio


d = {1: 'A', 2: 'B', 3:'Ә'}

async def scheduled(wait_for):
	print('Запуск создания интерната')
	while True:
		await asyncio.sleep(wait_for)
		for klass in range(7, 12):
			for letter in range(1, 4):
				newklass = str(klass) + d[letter]
				day = datetime.date.today().isoformat()	
				if not await sqlite_db.check_internat_req_food_command(day):
					await sqlite_db.internat_make_command(day)

		for klass in range(7, 12):
			for letter in range(1, 4):
				newklass = str(klass) + d[letter]
				today = datetime.date.today()
				tomorrow = today + datetime.timedelta(days=1)
				day = tomorrow
				if not await sqlite_db.check_internat_req_food_command(day):
					await sqlite_db.internat_make_command(day)
    	#print('meow')
    #await sqlite_db.check_internat_req_food_command(klass, data):



async def send_food(wait_for):
	print('запуск автоеды')
	while True:
		await asyncio.sleep(wait_for)
		date = datetime.datetime.today()
		date = str(date.strftime('%H:%M'))
		#date = int(date[1])	
		if date == '8:20':
			await bot.send_message(-821666496, f'питание на сегодня {day}:')
			day = datetime.date.today().isoformat()
			for klass in range(7, 12):
				for letter in range(1, 4):
					newklass = str(klass) + d[letter]
					if await sqlite_db.auto_food(day):
						read = await sqlite_db.get_full_food_command(day, newklass)
						#print(newklass)
						#print(read)
						if read != None:
							for ret in read:
								await bot.send_message(-821666496, f'' + 
									f'класс: {ret[0]}' +
									f'\nполных: {ret[1]}' +
									f'\nнеполных: {ret[2]}')
					weekday = datetime.datetime.today().weekday()	
					if weekday != 5 and weekday != 6:
						read = sqlite_db.internat_read_byday_command(day)
						for ret in read:
							await bot.send_message(-821666496, f'Питание интерната: +' +
								f'Первый завтрак: {ret[0]}' +
								f'Второй завтрак: {ret[1]}' +
								f'Обед: {ret[2]}' +
								f'Полдник: {ret[3]}' +
								f'Первый ужин: {ret[4]}' +
								f'Второй ужин: {ret[5]}'
								)
			await bot.send_message(-821666496, 'Бот отправил заявки и спит')
			await asyncio.sleep(10000)

async def anti_starosta(wait_for):
	print('запуск антистаросты')
	while True:
		await asyncio.sleep(wait_for)
		date = datetime.datetime.today()
		date = str(date.strftime('%H:%M'))
		#date = int(date[1])
		weekday = datetime.datetime.today().weekday()
		if weekday != 5 and weekday != 6:
			if date == '08:00' or date == '08:05' or date == '08:10' or date == '08:15' or date == '08:20':
				day = datetime.date.today().isoformat()
				for klass in range(7, 12):
					for letter in range(1, 4):
						newklass = str(klass) + d[letter]
						if not await sqlite_db.get_food(day, newklass):
							starosta_id = await sqlite_db.get_starosta(newklass)
							await bot.send_message(starosta_id, f'Сделай заявку')
				await bot.send_message(-821666496, 'ушел спать')
				await asyncio.sleep(30)


async def auto_norm_klass(wait_for):
	print('запуск замены класса')
	while True:
		await asyncio.sleep(wait_for)
		read = await sqlite_db.check_food_klass()
		for ret in read:
			if len(ret[0]) > 3:
				await sqlite_db.change_klass_to_norm(ret)