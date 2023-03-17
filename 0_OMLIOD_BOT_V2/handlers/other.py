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
		if date == '08:20':
			chats = [-821666496, -855152164]
			for x in chats:
				#da
				weekday = datetime.datetime.today().weekday()	
				day = datetime.date.today().isoformat()
				#ОБЫЧНАЯ ЕДА
				if weekday != 5 and weekday != 6:
					await bot.send_message(x, f'питание на сегодня {day}:')
					for klass in range(7, 12):
						for letter in range(1, 4):
							newklass = str(klass) + d[letter]
							if await sqlite_db.auto_food(day):
								read = await sqlite_db.sql_read_food_by_day(day)
								#print(newklass)
								#print(read)
								if read != None:
									for ret in read:
										await bot.send_message(x, f'' + 
											f'класс: {ret[0]}' +
											f'\nполных: {ret[1]}' +
											f'\nнеполных: {ret[2]}')
	
	
	
				#ИНТЕРНАТ
				read2 = await sqlite_db.read_internat_req_food_command(day)
				for ret in read2:
					await bot.send_message(x, f'Питание интерната:\n' +
						f'Первый завтрак: {ret[0]}\n' +
						f'Второй завтрак: {ret[1]}\n' +
						f'Обед: {ret[2]}\n' +
						f'Полдник: {ret[3]}\n' +
						f'Первый ужин: {ret[4]}\n' +
						f'Второй ужин: {ret[5]}\n'
								)		
	
	
				await bot.send_message(x, 'Бот отправил заявки и спит')
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
			if date == '08:00' or date == '08:05' or date == '08:10' or date == '08:15' or date == '08:20' or date == '10:30' or date == '11:30':
				day = datetime.date.today().isoformat()
				for klass in range(7, 12):
					for letter in range(1, 4):
						newklass = str(klass) + d[letter]
						if not await sqlite_db.get_food(day, newklass):
							starosta_id = await sqlite_db.get_starosta(newklass)
							if starosta_id != []:
								#ТАК И НАДО, НЕ УБИРАТЬ !!!!!!!!!!
								starosta_id = starosta_id[0]
								starosta_id = starosta_id[0]
								await bot.send_message(starosta_id, f'Сделай заявку на сегодня', reply_markup = kb.button_case_client)
								await bot.send_message(-821666496, f'{starosta_id} сделай заявку')
							print(starosta_id)
							
							
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
				await bot.send_message(-821666496, f'поменял класс {ret}')




async def isate_talon(wait_for):
	print('запуск поел ли')
	while True:
		await asyncio.sleep(wait_for)
		date = datetime.datetime.today()
		date = str(date.strftime('%H:%M'))
		#date = int(date[1])
		#da
		weekday = datetime.datetime.today().weekday()	
		day = datetime.date.today().isoformat()
		#ОБЫЧНАЯ ЕДА
		if weekday != 5 and weekday != 6:	
			if date == '13:30':
				await sqlite_db.update_eat()
				await bot.send_message(-821666496, f'Отметил поевших')
				eaters = await sqlite_db.get_eaters()
				for ret in eaters:
					await sqlite_db.save_eaters(ret[0], ret[1],ret[2], day, ret[3])
				await asyncio.sleep(10000)
		



async def delete_talon(wait_for):
	print('запуск удаления талонов')
	while True:
		await asyncio.sleep(wait_for)
		date = datetime.datetime.today()
		date = str(date.strftime('%H:%M'))
		#date = int(date[1])
		#da
		weekday = datetime.datetime.today().weekday()	
		day = datetime.date.today().isoformat()
		#ОБЫЧНАЯ ЕДА
		if weekday != 5 and weekday != 6:	
			if date == '6:00':
				await sqlite_db.delete_talons()
				await bot.send_message(-821666496, f'Удалил талоны')

				await asyncio.sleep(10000)
			


