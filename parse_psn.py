import requests
from bs4 import BeautifulSoup
import json

def parse_psn_store():
    url = 'https://store.playstation.com/en-us/grid/STORE-MSF75508-PSARSAVE20DISC/1'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    games = []
    
    # Здесь нужно обновить селекторы на актуальные для PSN Store Turkey
    for item in soup.select('.some-selector'):
        title = item.select_one('.title-selector').get_text(strip=True)
        current_price = item.select_one('.current-price-selector').get_text(strip=True)
        old_price = item.select_one('.old-price-selector').get_text(strip=True)
        discount_percentage = item.select_one('.discount-selector').get_text(strip=True)
        end_date = item.select_one('.end-date-selector').get_text(strip=True)
        game_link = item.select_one('a')['href']

        games.append({
            'title': title,
            'current_price': current_price,
            'old_price': old_price,
            'discount_percentage': discount_percentage,
            'end_date': end_date,
            'link': game_link
        })
    
    with open('psn_games.json', 'w', encoding='utf-8') as json_file:
        json.dump(games, json_file, ensure_ascii=False, indent=4)
    
    print('Data parsed and saved to psn_games.json')

if __name__ == '__main__':
    parse_psn_store()