import httpx
import json
import asyncio
from bs4 import BeautifulSoup
from loguru import logger
from random import shuffle
import json
import time


with open('parse_config.json', 'r') as file:
    config = json.load(file)


async def clean_price(price_str: str) -> float:
    cleaned_price = price_str.replace('\xa0', '').replace('TL', '').replace('.', '').strip()
    
    cleaned_price = cleaned_price.replace(',', '.')
    
    if '.' in cleaned_price:
        integer_part, decimal_part = cleaned_price.split('.', 1)
        integer_part = ''.join(filter(str.isdigit, integer_part))
        decimal_part = ''.join(filter(str.isdigit, decimal_part))
        cleaned_price = integer_part + '.' + decimal_part
    else:
        cleaned_price = ''.join(filter(str.isdigit, cleaned_price))
    
    return float(cleaned_price) if cleaned_price else 0.0


async def get_proxy_list() -> list[str]:
    logger.debug('Start read proxy file func with params: proxy.txt')
    try:
        with open('proxy.txt', 'r', encoding='utf-8') as file_with_proxy:
            proxy_list = file_with_proxy.readlines()
        logger.debug(f'Completed read proxy file func, return value: {proxy_list}')
        return proxy_list
    except Exception as e:
        logger.error(f'Error when read proxy file func: {e}')
        raise e


async def get_proxy(proxy_list: list[str], proxy_id: int) -> tuple[str, int] | tuple[None, int]:
    logger.debug(f'Start get proxy func with params: {proxy_id}')
    try:
        if proxy_list == []:
            return None, 0
        if proxy_id >= len(proxy_list) - 1:
            proxy_id = 0
        else:
            proxy_id += 1
        logger.debug(f'Completed get proxy, return value: {proxy_list[proxy_id]}, {proxy_id}')
        return proxy_list[proxy_id].strip(), proxy_id
    except Exception as e:
        logger.error(f'Error when get proxy func {e}')
        raise e


async def fetch_game_data(page_number: int, proxy: str | None):
    url = f'https://store.playstation.com/en-tr/category/1bc5f455-a48e-43d1-b429-9c52fa78bb4d/{page_number}'

    async with httpx.AsyncClient(proxies=proxy) as client:
        try:
            response = await client.get(url)
            logger.debug(f'Fetched page {page_number}: {response.status_code}')
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f'Error when fetching page {page_number}: {e}')
            return None


async def fetch_discount_data(link: str, proxy: str | None):
    async with httpx.AsyncClient(proxies=proxy) as client:
        try:
            response = await client.get(link)
            logger.debug(f'Fetched discount page: {link} - Status: {response.status_code}')
            if response.status_code != 200:
                return None
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f'Error when fetching discount page: {link} - {e}')
            return None


async def main():
    psn_games = []
    proxy_list = await get_proxy_list()
    proxy, proxy_id = await get_proxy(proxy_list, 0)
    discount_request_count = 0
    
    for i in range(1, 244):
        if i % config['replace_proxy_count'] == 0:
            proxy, proxy_id = await get_proxy(proxy_list, proxy_id)

        response = None
        attempts = 0
        while response is None and attempts < config['retry_attemps']:
            response = await fetch_game_data(i, proxy)
            if response is None:
                logger.debug(f'Retrying page {i} with new proxy.')
                proxy, proxy_id = await get_proxy(proxy_list, proxy_id)
                attempts += 1

        if response is None:
            logger.warning(f'Skipping page {i} after {config['retry_attemps']} failed attempts.')
            continue
        
        games = response.find_all('li', class_='psw-l-w-1/2@mobile-s psw-l-w-1/2@mobile-l psw-l-w-1/6@tablet-l psw-l-w-1/4@tablet-s psw-l-w-1/6@laptop psw-l-w-1/8@desktop psw-l-w-1/8@max')
        
        if config['shuffle_game']:
            shuffle(games)
        
        for game in games:
            title = game.find('span', class_='psw-t-body psw-c-t-1 psw-t-truncate-2 psw-m-b-2').text
            discount_badge = game.find('span', class_='psw-body-2 psw-badge__text psw-badge--none psw-text-bold psw-p-y-0 psw-p-2 psw-r-1 psw-l-anchor')
            if discount_badge is None:
                continue

            discount = discount_badge.text
            link = 'https://store.playstation.com' + game.find('a')['href']

            discount_page_soup = None
            attempts = 0
            while discount_page_soup is None and attempts < config['retry_attemps']:
                discount_request_count += 1
                if discount_request_count % config['replace_proxy_count'] == 0:
                    proxy, proxy_id = await get_proxy(proxy_list, proxy_id)
                discount_page_soup = await fetch_discount_data(link, proxy)
                attempts += 1

            if discount_page_soup is None:
                logger.warning(f'Skipping link {link} after {config['retry_attemps']} failed attempts.')
                continue

            discount_expire = discount_page_soup.find('span', {"data-qa": "mfeCtaMain#offer0#discountDescriptor"}, class_='psw-c-t-2')
            if discount_expire is None:
                continue
            
            old_price = await clean_price(discount_page_soup.find('span', {"data-qa": "mfeCtaMain#offer0#originalPrice"}, class_='psw-t-title-s psw-c-t-2 psw-t-strike').text)
            
            new_price = await clean_price(discount_page_soup.find('span', {"data-qa": "mfeCtaMain#offer0#finalPrice"}, class_='psw-t-title-m psw-m-r-4').text)

            discount_expire_text = discount_expire.text

            psn_game = {
                'title': title,
                'discount': discount,
                'old_price': old_price,
                'new_price': new_price,
                'discount_expire': discount_expire_text,
                'link': link,
            }

            psn_games.append(psn_game)

            with open('psn_games.json', 'w', encoding='utf-8') as file:
                json.dump(psn_games, file, ensure_ascii=False, indent=4)
                
            time.sleep(config['wait_response'])
            
        logger.debug(f'Page {i} parse completed!')

    logger.debug('Parse completed!')


if __name__ == "__main__":
    asyncio.run(main())
