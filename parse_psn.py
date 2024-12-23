import httpx
import json
import asyncio
from bs4 import BeautifulSoup
import random
import time

psn_games = []

async def fetch_game_data(page_number):
    url = f'https://store.playstation.com/en-tr/category/1bc5f455-a48e-43d1-b429-9c52fa78bb4d/{page_number}'
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            print(f"Fetched page {page_number}: {response.status_code}")
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except:
            print('Error when parse page')

async def fetch_discount_data(link):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(link)
            print(f"Fetched discount page: {link} - Status: {response.status_code}")
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except:
            print('Error nwhen parse discount')

async def main():
    tasks = []
    
    for i in range(1, 244):
        tasks.append(await fetch_game_data(i))
        await asyncio.sleep(0)
    
    pages = tasks

    for soup in pages:
        if soup is None:  # Проверяем, был ли получен ответ
            continue

        games = soup.find_all('li', class_='psw-l-w-1/2@mobile-s psw-l-w-1/2@mobile-l psw-l-w-1/6@tablet-l psw-l-w-1/4@tablet-s psw-l-w-1/6@laptop psw-l-w-1/8@desktop psw-l-w-1/8@max')
        
        if not games:
            print(f"No games found on page {soup}")

        for game in games:
            title = game.find('span', class_='psw-t-body psw-c-t-1 psw-t-truncate-2 psw-m-b-2').text

            discount_badge = game.find('span', class_='psw-body-2 psw-badge__text psw-badge--none psw-text-bold psw-p-y-0 psw-p-2 psw-r-1 psw-l-anchor')
            if discount_badge is None:
                continue

            discount = discount_badge.text
            link = 'https://store.playstation.com' + game.find('a')['href']

            discount_page_soup = await fetch_discount_data(link)

            if discount_page_soup is None:
                continue

            discount_expire = discount_page_soup.find('span', {"data-qa": "mfeCtaMain#offer0#discountDescriptor"}, class_='psw-c-t-2')
            if discount_expire is None:
                continue

            discount_expire_text = discount_expire.text

            psn_game = {
                'title': title,
                'discount': discount,
                'discount_expire': discount_expire_text,
                'link': link,
            }

            psn_games.append(psn_game)

    print('Page parse completed!')

    with open('psn_games.json', 'w', encoding='utf-8') as file:
        json.dump(psn_games, file, ensure_ascii=False, indent=4)

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
