import aiohttp
import os
import asyncio

from bot_config import KINOPOISK_API_KEY, GOOGLE_SEARCH_API_KEY


async def fetch_kinopoisk_info(movie_title):
    url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={movie_title}'    
    headers = {
        'X-API-KEY': KINOPOISK_API_KEY,
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data['films']:
                    film = data['films'][0]
                    title = film.get('nameRu', 'N/A')
                    year = film.get('year', 'N/A')
                    country = film.get('countries', [{'country': 'N/A'}])[0]['country']
                    kp_rating = film.get('rating', 'N/A')
                    poster = film.get('posterUrl', 'N/A')
                    kinopoisk_url = f"https://www.kinopoisk.ru/film/{film.get('filmId', 'N/A')}/"
                    return (f"Название: {title}\n"
                            f"Год выпуска: {year}\n"
                            f"Страна: {country}\n"
                            f"Рейтинг КП: {kp_rating}\n"
                            f"Постер: {poster}\n"
                            f"URL: {kinopoisk_url}")                
                else:
                    return "Такого фильма нет на кинопоиске"
            else:
                return "Ошибка сбора информации о фильме"


async def fetch_movie_sources(movie_title):
    base_url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={movie_title}'
    headers = {
        'X-API-KEY': KINOPOISK_API_KEY,
        'Content-Type': 'application/json'
    }

    serper_url = 'https://google.serper.dev/search'
    serper_headers = {
        'X-API-KEY': GOOGLE_SEARCH_API_KEY,
        'Content-Type': 'application/json'
    }
    serper_payload = {
        'q': f'{movie_title} смотреть онлайн бесплатно'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data['films']:
                    film = data['films'][0]
                    film_id = film.get('filmId')
                else:
                    return None
            else:
                return None

        if film_id:
            url = f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}/external_sources?page=1'
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    sources = data.get('items', [])
                    if not sources:
                        sources_info = "Источники не найдены."
                    else:
                        sources_info = "Официальные источники:\n"
                        for source in sources:
                            platform = source.get('platform', 'N/A')
                            url = source.get('url', 'N/A')
                            sources_info += f"{platform}\nURL: {url}\n\n"
                else:
                    sources_info = "Не получилось получить информацию об источниках"
        else:
            sources_info = "Не удалось найти ID фильма"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(serper_url, headers=serper_headers, json=serper_payload) as response:
                if response.status == 200:
                    serper_data = await response.json()
                    search_results = serper_data.get('organic', [])[:4]
                    if search_results:
                        serper_info = "Пиратские источники:\n"
                        for result in search_results:
                            title = result.get('title', 'N/A')
                            link = result.get('link', 'N/A')
                            serper_info += f"{title}\nURL: {link}\n\n"
                    else:
                        serper_info = "Ссылки не найдены."
                else:
                    serper_info = "Не получилось получить информацию из Google."
        
        return f"{sources_info}\n{serper_info}"