from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from httpx import AsyncClient


browser = webdriver.Chrome()
browser.get('https://store.playstation.com/en-tr/category/1bc5f455-a48e-43d1-b429-9c52fa78bb4d/1')

game = browser.find_element(By.CSS_SELECTOR, 'a[class="psw-link psw-content-link"]')
game.click()

soup = BeautifulSoup(browser.page_source, 'html.parser')

discount_expire = soup.find('span', {"data-qa": "mfeCtaMain#offer0#discountDescriptor"}, class_='psw-c-t-2').text

print(discount_expire)
