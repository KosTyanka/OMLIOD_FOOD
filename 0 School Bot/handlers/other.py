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
  while True:
    await asyncio.sleep(wait_for)
    day = datetime.date.today().isoformat()
    for klass in range(7, 12):
    	for letter in range(1, 4):
    		newklass = str(klass) + d[letter]
    		if not await sqlite_db.check_internat_req_food_command(newklass, day):
    			await sqlite_db.internat_make_command(newklass, day)
    	#print('meow')
    #await sqlite_db.check_internat_req_food_command(klass, data):


async def send_food(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		date = datetime.datetime.today()
		date = str(date.strftime('%H:%M'))
		date = int(date[1])
		if date == 9:
			day = datetime.date.today().isoformat()
			for klass in range(7, 12):
				for letter in range(1, 4):
					newklass = str(klass) + d[letter]
					if not await sqlite_db.check_req_food_command(newklass, day):
						read = await sqlite_db.get_full_food_command(day)
						if read != None:

							for ret in read:
								await bot.send_message(-855152164, f'Питание классов на {day}: \n' + 
									f'класс: {ret[0].strip("[()]")}' +
									f'\nполных: {ret[1]}' +
									f'\nнеполных: {ret[2]}')