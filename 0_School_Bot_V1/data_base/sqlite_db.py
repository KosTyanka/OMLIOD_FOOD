import sqlite3 as sq
from create_bot import dp, bot
from datetime import datetime 

def sql_start():
	#СОЗДАНИЕ ПЕРЕМЕННЫХ
	global base, cur
	global req_base, req_cur
	#СВЯЗЬ С БАЗАМИ И КУРСОРЫ
	base = sq.connect('OMLIOD.db')
	cur = base.cursor()
	req_base = sq.connect('foodtable.db')
	req_cur = req_base.cursor()
	#СОЗДАНИЕ БАЗ ЕСЛИ НЕ СУЩЕСТВУЮТ
	if base:
		print('Data base connected OK')
	base.execute('CREATE TABLE IF NOT EXISTS menu(phone TEXT, user_id TEXT PRIMARY KEY,nameOf TEXT, class TEXT)')
	base.commit()
	base.execute('CREATE TABLE IF NOT EXISTS starosty(class TEXT, user_id TEXT PRIMARY KEY, phone_number TEXT)')
	base.commit()
	if req_base:
		print('ПИТАНИЕ НА МЕСТЕ OK')
	req_base.execute('CREATE TABLE IF NOT EXISTS food(class TEXT, poln INT, nepoln INT, day DATE)')
	req_base.commit()
	req_base.execute('CREATE TABLE IF NOT EXISTS internat(firstzavtrak INT, secondzavtrak INT, obed INT, poldnik INT, firstuzhin INT, seconduzhin INT,day DATE)')
	req_base.commit()
	req_base.execute('CREATE TABLE IF NOT EXISTS absent(class TEXT, whomissing TEXT, day DATE, why TEXT)')
	req_base.commit()



async def sql_add_command(state):
	async with state.proxy() as data:
		cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', tuple(data.values()))
		base.commit()

async def req_add_command(state):
	async with state.proxy() as data:
		req_cur.execute('INSERT INTO food VALUES (?, ?, ?, ?)', tuple(data.values()))
		req_base.commit()

async def get_all_id():
	with base:
		result = cur.execute('SELECT user_id FROM menu').fetchall()
		return result

async def make_starosta(klass, user_id, phone_number):
	with base:
		cur.execute('INSERT INTO starosty VALUES (?, ?, ?)', (klass, user_id, phone_number))
		base.commit()




async def internat_make_command(day):
	req_cur.execute('INSERT INTO internat VALUES (0, 0, 0, 0, 0, 0, ?)', (day,))
	req_base.commit()

async def internat_change_command(food, number, day):
	req_cur.execute(f'UPDATE internat SET {food} = ? WHERE day = ?', (number, day))
	req_base.commit()

async def internat_read_byday_command(day):
	return req_cur.execute('SELECT * FROM internat where day = ?', (day,)).fetchall()
#async def sql_read(message):
#	for ret in cur.execute('SELECT * FROM menu').fetchall():
		#await bot.send_photo(message.from_user.id, ret[0], f'Вопрос: {ret[1]}\nКомпания: {ret[2]}\nid:\nДата вопроса: {ret[-1]}' )

async def sql_read_food(message):
	return req_cur.execute('SELECT * FROM food').fetchall()

async def sql_read_food_by_day(day):
	return req_cur.execute('SELECT * FROM food WHERE day = ?', (day,)).fetchall()

async def internat_read_food(message):
	return req_cur.execute('SELECT * FROM internat').fetchall()

#async def sql_delete_command(data):
#	cur.execute('DELETE FROM menu WHERE phone == ?', (data,))
#	base.commit()


async def food_delete_command(klass, day):
	with req_base:
		req_cur.execute('DELETE FROM food WHERE class == ? AND day == ?', (klass, day))
		req_base.commit()

async def internat_delete_command(klass, day):
	with req_base:
		req_cur.execute('DELETE FROM internat WHERE class == ? AND day == ?', (klass,day))
		req_base.commit()


async def check_food_klass():
	with req_base:
		result = req_cur.execute('SELECT class FROM food').fetchall()
		return result

async def change_klass_to_norm(klass):
	with req_base:
		newklass = klass[0].strip("[('')]")
		newklass = newklass[:3:]
		if newklass[2] == "'":
			newklass = newklass[:2]
		print(newklass)
		req_cur.execute('UPDATE food SET class = ? WHERE class = ?', (newklass,klass[0]))
		req_base.commit()


async def sql_get_command(data):
	return cur.execute('SELECT phone FROM menu WHERE user_id == ?', (data,)).fetchall()

async def class_get_command(data):
	result = cur.execute('SELECT class FROM menu WHERE user_id == ?', (data,)).fetchall()
	return result[0]

async def user_exists(user_id):
    """ Проверяем есть ли такой пользователь в БД """
    with base:
        result = cur.execute('SELECT * FROM menu WHERE user_id = ?', (user_id,)).fetchall()
        return bool(len(result))

async def get_req_food_command(klass, data):
	with req_base:
		result = req_cur.execute('SELECT poln, nepoln FROM food WHERE class==? AND day == ?', (klass, data,)).fetchone()
		return result


async def get_full_food_command(data, klass):
	with req_base:
		result = req_cur.execute('SELECT * FROM food WHERE day == ? AND class == ?', (data, klass,)).fetchall()
		return result


async def check_req_food_command(klass, data):
	with req_base:
		result = req_cur.execute('SELECT poln, nepoln FROM food WHERE class==? AND day == ?', (klass, data,)).fetchone()
		if result != None:
			return bool(len(result))
		else:
			return False



async def check_internat_req_food_command(data):
	with req_base:
		result = req_cur.execute('SELECT * FROM internat WHERE day == ?', (data,)).fetchone()
		if result != None:
			return bool(len(result))
		else:
			return False

async def read_internat_req_food_command(data):
	with req_base:
		result = req_cur.execute('SELECT * FROM internat WHERE day = ?', (data,)).fetchall()
		return result


async def change_klass(klass, userid):
	with base:
		cur.execute('UPDATE menu SET class = ? WHERE user_id = ?', (klass, userid))
		base.commit()




async def auto_food(data):
	with req_base:
		result = req_cur.execute('SELECT poln, nepoln FROM food WHERE day == ?', (data,)).fetchall()
		if result != None:
			return True
		else:
			return False

async def get_food(data, klass):
	with req_base:
		result = req_cur.execute('SELECT poln, nepoln FROM food WHERE day = ? and class = ?', (data, klass)).fetchall()
		#print(result)
		if not result:
			print(1)
			return False
		if result != None:
			return True
		else:
			return False

async def get_starosta(klass):
	with base:
		result = cur.execute('SELECT user_id FROM starosty WHERE class == ?', (klass,)).fetchall()
		return result


async def test(data):
	with req_base:
		result = req_cur.execute('SELECT class FROM food WHERE day == ?', (data,)).fetchall()
	if result != None:
		result = str(result[0])
		return result[5:7]
	else:
		return False



#async def check_sql_add_command(state):
#	async with state.proxy() as data:
#		check_cur.execute('INSERT INTO stat VALUES (?, ?, ?, ?)', tuple(data.values()))
#		check_base.commit()
#
#async def user_exists(user_id):
#    """ Проверяем есть ли такой пользователь в БД """
#    with check_base:
#        result = check_cur.execute('SELECT * FROM stat WHERE user_id = ?', (user_id,)).fetchall()
#        return bool(len(result))
#
#async def get_phone_number(user_id):
#    """ Получить телефон """
#    with check_base:
#        result = check_cur.execute('SELECT phone_number FROM stat WHERE user_id = ?', (user_id,)).fetchall()
#        return result
#
#
#async def queue_add_command(name, user_id, phone_number, vremya):
#	with queue_base:
#		queue_cur.execute('INSERT or IGNORE INTO queue VALUES(?, ? , ?, ?, ?, ?)', (name, user_id, phone_number, vremya, False, 0))
#		queue_base.commit()
#
#
#async def queue_read_undone_command(message):
#	return queue_cur.execute('SELECT * FROM queue WHERE isdone == 0').fetchall()
#
#async def queue_worked_command(data, userid):
#	queue_cur.execute('UPDATE queue SET isdone = 1, whoworked = ? WHERE vremya == ?', (userid, data,))
#	#queue_cur.execute('UPDATE queue SET isdone = 1, whoworked = id WHERE vremya == ?', (data,))
#	queue_base.commit()
#
#async def get_admins_command():
#	return admins_cur.execute('SELECT name FROM admins').fetchall()
#
#async def get_admins_byphone_command(phone):
#	name_of_manager = admins_cur.execute('SELECT name FROM admins WHERE phone_number = ?', (phone,)).fetchone()
#	return name_of_manager
#
#
#async def set_admin_command(admin_name, userid):
#	with check_base:
#		check_cur.execute('UPDATE stat SET admin = ? WHERE user_id == ?', (admin_name, userid))
##async def sql_add_command(state):
##	async with state	#