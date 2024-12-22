import requests
from bs4 import BeautifulSoup
import json

# URL PSN Store Turkey (пример)
url = 'https://store.playstation.com/tr-tr/home/games'

# Отправляем GET-запрос
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Список для хранения данных
discounted_games = []

# Находим элементы с информацией о скидках
for game in soup.find_all('div', class_='some-class-for-game'):
    title = game.find('h3', class_='game-title').text.strip()
    current_price = game.find('span', class_='current-price').text.strip()
    old_price = game.find('span', class_='old-price').text.strip()
    discount_percentage = game.find('span', class_='discount-percentage').text.strip()
    end_date = game.find('span', class_='end-date').text.strip()

    discounted_games.append({
        'title': title,
        'current_price': current_price,
        'old_price': old_price,
        'discount_percentage': discount_percentage,
        'end_date': end_date
    })

# Сохраняем данные в JSON
with open('psn_games.json', 'w', encoding='utf-8') as f:
    json.dump(discounted_games, f, ensure_ascii=False, indent=4)

print("Данные успешно сохранены в psn_games.json")