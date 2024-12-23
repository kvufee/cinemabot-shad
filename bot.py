import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from db import init_db, get_history, get_stats, save_query
from utils import fetch_kinopoisk_info, fetch_movie_sources
from bot_config import BOT_TOKEN
from keyboard_markup import keyboard_markup


API_TOKEN = BOT_TOKEN
if not API_TOKEN:
    raise ValueError("No BOT_TOKEN provided")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который поможет найти информацию где посмотреть фильм по запросу.", reply_markup=keyboard_markup)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Чтобы найти фильм просто напиши его название в чат", reply_markup=keyboard_markup)


@dp.message_handler(commands=['history'])
async def send_history(message: types.Message):
    history = await get_history(message.from_user.id)
    if history:
        await message.reply("\n".join(history), reply_markup=keyboard_markup)
    else:
        await message.reply("Вы ничего не искали", reply_markup=keyboard_markup)


@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    stats = await get_stats(message.from_user.id)
    if stats:
        await message.reply("\n".join(stats), reply_markup=keyboard_markup)
    else:
        await message.reply("Нет элементов", reply_markup=keyboard_markup)


@dp.message_handler()
async def handle_message(message: types.Message):
    if message.text == 'Начать':
        await send_welcome(message)
    elif message.text == 'Помощь':
        await send_help(message)
    elif message.text == 'История':
        await send_history(message)
    elif message.text == 'Статистика':
        await send_stats(message)
    else:
        await search_movie(message)


async def search_movie(message: types.Message):
    movie_info = await fetch_kinopoisk_info(message.text)
    sources_info = await fetch_movie_sources(message.text)
    await save_query(message.from_user.id, message.from_user.username, message.text)
    await message.reply(movie_info, reply_markup=keyboard_markup)
    if sources_info:
        await message.reply(sources_info, reply_markup=keyboard_markup)


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    executor.start_polling(dp, skip_updates=True)