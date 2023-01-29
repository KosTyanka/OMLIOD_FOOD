from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from data_base import sqlite_db
'''*****************************КОНСТРУКТОР КНОПОК*****************'''
#клиент

button_phone_number = KeyboardButton('Предоставить номер телефона', request_contact =True)
reg_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_phone_number)

button_hi = KeyboardButton('Привет! 👋')
#button_question = KeyboardButton('/Задать_вопрос')
button_help = KeyboardButton('/Доступные_команды')
button_info = KeyboardButton('/Вопросы_и_Об_авторе')
button_request = KeyboardButton('/Отправить_заявку')
button_check = KeyboardButton('/Проверить_заявку')

button_confirm_en = KeyboardButton('/confirm')
button_confirm_rus = KeyboardButton('/Все_верно')
button_cancel_en = KeyboardButton('/cancel')
button_cancel_rus = KeyboardButton('/отмена') 

class_7A = KeyboardButton('/7A')
class_7B = KeyboardButton('/7B')
buttons7 = [class_7A, class_7B]
class_8A = KeyboardButton('/8A')
class_8Z = KeyboardButton('/8Ә')
class_8B = KeyboardButton('/8B')
buttons8 = [class_8A, class_8Z, class_8B]
class_9A = KeyboardButton('/9A')
class_9Z = KeyboardButton('/9Ә')
class_9B = KeyboardButton('/9B')
buttons9 = [class_9A, class_9Z, class_9B]
class_10A = KeyboardButton('/10A')
class_10B = KeyboardButton('/10B')
buttons10 = [class_10A, class_10B]
class_11A= KeyboardButton('/11A')
class_11B = KeyboardButton('/11B')
buttons11 = [class_11A, class_11B]

greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_hi)
greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb1.add(button_hi)
greet_kb2 = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
)
greet_kb2.add(button_hi)
quest_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
)

double_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
)
# INLINE КНОПКИ
urlkb = InlineKeyboardMarkup(row_width=1)
url_Button = InlineKeyboardButton(text="Ссылка", url='https://docs.google.com/document/d/1jy5NAJ493ILbv98v-NBJjuDgSO44x4lO/edit?usp=sharing&ouid=114159890370412944594&rtpof=true&sd=true')
url_Button2 = InlineKeyboardButton(text="Скачка файла", url='https://drive.google.com/uc?export=download&confirm=no_antivirus&id=1jy5NAJ493ILbv98v-NBJjuDgSO44x4lO')
urlkb.add(url_Button, url_Button2)

food_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Удалить заявку', callback_data =f'delete'))
#food_button_del = InlineKeyboardButton(text='Удалить заявку', callback_data =f'udalit')
#food_kb.add(food_button_del)

adminskb = InlineKeyboardMarkup(row_width=2)
async def makebuttons():
	read = await sqlite_db.get_admins_command()
	admins = [ret for ret in read]
	for i in admins:
		i = InlineKeyboardButton(text = str(i), callback_data = f'admin {i} ' + '|' + str(message.from_user.id) )
		adminskb.add(i)
	#or ret in read:


#КОНЕЦ INLINE КНОПОК


#Админ
button_admin_help = KeyboardButton('/Что_мне_делать?')
button_admin_commands = KeyboardButton('/Команды_бота')
button_admin_stat = KeyboardButton('/Получить_питание')


admin_panel_kb = ReplyKeyboardMarkup(
	resize_keyboard=True, one_time_keyboard=True
	)
button_load = KeyboardButton('/Задать_вопрос')
button_delete = KeyboardButton('/Удалить')
button_call = KeyboardButton('/Заказать_звонок')


'''**************************** САМИ КНОПКИ ***************************'''

button_case_client = ReplyKeyboardMarkup(resize_keyboard=True).add(button_help).add(button_info).add(button_request).add(button_check)

buttons_confirm = ReplyKeyboardMarkup(resize_keyboard=True).add(button_confirm_rus).add(button_cancel_rus)

#quest_kb.add(button_question)

double_kb.add(button_help)

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_admin_help).add(button_admin_commands).add(button_admin_stat).add(button_info)
#admin_panel_kb.add(button_admin_help).add(button_admin_questions)
#admin_panel_kb.add(button_admin_answer, button_admin_help, button_admin_delete)


class_select_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons7).add(*buttons8).add(*buttons9).add(*buttons10).add(*buttons11)