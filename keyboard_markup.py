from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_start = KeyboardButton('Начать')
button_help = KeyboardButton('Помощь')
button_history = KeyboardButton('История')
button_stats = KeyboardButton('Статистика')

keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(button_start, button_help, button_history, button_stats)
