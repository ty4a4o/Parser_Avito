import requests
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random; 
from selenium import webdriver
from selenium.webdriver.common.by import By

# URL
url = "https://www.avito.ru/ufa/remont_i_stroitelstvo/kompleks_dom_s_baney_i_chanom_pod_klyuch._barnhouse_53._tsena_za_m2_7472027137"

# Генерируем случайный реалистичный User-Agent
ua = UserAgent()
headers = {
    "User-Agent": ua.random,
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/ ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Задержка перед запросом
time.sleep(random.uniform(1, 7))

# Отправляем GET-запрос
response = requests.get(url, headers=headers)

# Проверяем успешность запроса
if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Заголовок
    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.text.strip()
        print(f"Заголовок объявления: {title}")
    else:
        print("Заголовок не найден")

    # Цена
    price_tag = soup.find("div", {"data-marker": "item-view/item-price-container"})
    if price_tag:
        price = price_tag.text.strip()
        print(f"Цена объявления: {price}")
    else:
        print("Цена не найдена")

    # Описание
    description_tag = soup.find("div", {"data-marker": "item-view/item-description"})
    if description_tag:
        description = description_tag.text.strip()
        print(f"Описание: {description}")
    else:
        print("Описание не найдено")

    # Фотографии
    image_tag = soup.find('div', id='bx_item-gallery')
    if image_tag:
        Image = image_tag.get("src")
        print(f"Фото: {Image}")
    else:
        print("Фото не найдено")

    # Лайк
    like_tag = soup.find("button", {"data-marker": "item-view/favorite-button"})
    if like_tag:
        like = like_tag.text.strip()
        print(f"Описание: {like}")
    else:
        print("Описание не найдено")
    
    # Похожее
    same_tag = soup.find("h3", {"data-marker": "bx-recommendations-block-title"})
    if same_tag:
        same = same_tag.text.strip()
        print(f"Похожие объявления: {same}")
    else:
        print("Похожее не найдена")

    # Показать карту
    hide_map_tag = soup.find("a", {"data-text-open": "Узнать подробности"})
    if hide_map_tag:
        hide_map = hide_map_tag.text.strip()
        print(f"Описание: {hide_map}")
    else:
        print("Описание не найдено")

    # Кнопка вперед
    img_forward_tag = soup.find("div", {"area-label": "Вперёд"})
    if img_forward_tag:
        img_forward = img_forward_tag.text.strip()
        print(f"Кнопка вперед: {img_forward}")
    else:
        print("Кнопка вперед не найдено")

    # Кнопка назад
    img_back_tag = soup.find("div", {"area-label": "Назад"})
    if img_back_tag:
        img_back = img_back_tag.text.strip()
        print(f"Описание: {img_back}")
    else:
        print("Кнопка вперед не найдено")

# Обработка ошибок
elif response.status_code == 403:
    print("❌ Доступ запрещён. Попробуй использовать прокси или другой User-Agent.")
else:
    print(f"❌ Ошибка загрузки страницы. Код состояния: {response.status_code}")
