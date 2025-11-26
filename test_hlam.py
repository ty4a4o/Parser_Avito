# # Парсинг данных
# def parse_avito_page(url):
#     driver = setup_browser()
#     driver.get(url)
#     random_delay()

#     data = {}

#     # Заголовок
#     title_locators = [
#         '//h1[@data-marker="item-view/title-info"]',
#         # '//h1[contains(@class, "title-info__title")]'
#     ]
#     title_elem = try_find_element(driver, title_locators)
#     data["title"] = title_elem.text if title_elem else "Не найдено"

#     # Цена
#     price_locators = [
#         '//span[@class="FfCOp"]',
#         # '//div[@data-marker="item-view/item-price-container"]',
#         # '//span[contains(@class, "price-text")]'
#     ]
#     price_elem = try_find_element(driver, price_locators)
#     data["price"] = price_elem.text if price_elem else "Не найдено" 

#     if price_elem:
#     # Убираем пробелы
#         price_text = price_elem.text.replace('\u00A0', ' ').replace(' ', '') 
#         data["price"] = price_text
#     else:
#         data["price"] = "Не найдено"

#     # Описание
#     description_button_locators = [
#         '//a[contains(text(), "Читать полностью")]'
#     ]

#     # Поиск кнопки
#     button_elem = try_find_element(driver, description_button_locators)

#     # Нажатие на кнопку, если она найдена
#     if button_elem:
#         button_elem.click()
#         time.sleep(1)

#     description_locators = [
#         '//div[@data-marker="item-view/item-description"]',
#         # '//div[contains(@class, "item-description")]'
#     ]
#     description_elem = try_find_element(driver, description_locators)
#     data["description"] = description_elem.text if description_elem else "Не найдено"

#     # # Характеристики
#     # specs_locators = [
#     #     '//ul[@class="HRzg1"]',
#     #     # '//div[@class="item-params"]'
#     # ]
#     # specs_elem = try_find_element(driver, specs_locators)
#     # data["specs"] = specs_elem.text if specs_elem else "Не найдено"

#     # Характеристики
#     specs_button_locators = [
#         '//a[contains(text(), "Все характеристики")]'
#     ]

#     # Поиск кнопки
#     button_elem = try_find_element(driver, specs_button_locators)

#     # Нажатие на кнопку, если она найдена
#     if button_elem:
#         button_elem.click()
#         time.sleep(1)

#     # Теперь ищем характеристики
#     specs_locators = [
#         '//div[@data-marker="model-card/modification-specs"]',
#         # '//div[@class="item-params"]'
#     ]
#     specs_elem = try_find_element(driver, specs_locators)
#     data["specs"] = specs_elem.text if specs_elem else "Не найдено"

#     driver.back()
#     time.sleep(2)

#     # # Кнопка развертывания карты
#     # map_button_locators = [
#     #     '//a[contains(text(), "Показать на карте")]',
#     #     '//a[contains(text(), "Узнать подробности")]',
#     # ]

#     # # Поиск кнопки
#     # button_elem = try_find_element(driver, map_button_locators)

#     # # Нажатие на кнопку, если она найдена
#     # if button_elem:
#     #     button_elem.click()
#     #     time.sleep(1)
        
#         # не трогать
#     # map_button_locators = [
#     #     '//button[@data-marker="VznZr"]',
#     #     '//button[@data-marker="Civbl"]',
#     #     # '//button[contains(text(), "Показать на карте")]'
#     # ]

#     # map_container = [
#     #     '//ymaps[@class="ymaps-2-1-79-inner-panes")]',
#     # ]
#     # try:
#     #     map_container_elem = driver.find_element(driver, map_container)
#     # except:
#     #     print("Не удалось найти контейнер карты")
#     # exit()

#     # human_like_scroll(map_container_elem, driver, scrolls=4) # Скролл
#     # drag_map(driver, map_container_elem, offset_x=100, offset_y=0) # Тащить вправо
#     # drag_map(driver, map_container_elem, offset_x=0, offset_y=100) # Тащить вниз
#     # drag_map(driver, map_container_elem, offset_x=-100, offset_y=-100) # Тащить лево-право

#     # Фото (галерея)
#     photo_locators = [
#         '//div[@class="iAcbL"]//img', 
#         # '//li[@data-marker="image-preview/item"]//img',
#         # '//img[@class="image-frame__image"]'
#     ]
#     photo_elems = []
#     for locator in photo_locators:
#         try:
#             photos = WebDriverWait(driver, 5).until(
#                 EC.presence_of_all_elements_located((By.XPATH, locator))
#             )
#             photo_elems = [img.get_attribute("src") for img in photos]
#             break
#         except:
#             continue
#     data["photos"] = photo_elems or ["Фото не найдены"]

#     # # Переключение фото (вперед/назад)
#     # next_button_locators = [
#     #     '//button[@data-marker="image-frame/right-button"]',
#     #     # '//button[@aria-label="Следующее изображение"]'
#     # ]
#     # prev_button_locators = [
#     #     '//button[@data-marker="image-frame/left-button"]',
#     #     # '//button[@aria-label="Предыдущее изображение"]'
#     # ]

#     # next_button = try_find_element(driver, next_button_locators)
#     # prev_button = try_find_element(driver, prev_button_locators)

#     # if next_button:
#     #     next_button.click()
#     #     print("Кнопка 'Вперёд' найдена.")
#     #     time.sleep(1)
#     # if prev_button:
#     #     prev_button.click()
#     #     print("Кнопка 'Назад' найдена.")
#     #     time.sleep(1)

#     # Завершение работы
#     driver.quit()
#     return data

# # URL
# target_url = "https://www.avito.ru/ufa/odezhda_obuv_aksessuary/kedy_muzhskie_7644371830"

# # Вызов функции
# result = parse_avito_page(target_url)

# # Вывод результата
# print("\nРезультат парсинга:")
# for key, value in result.items():
#     print(f"{key.capitalize()}: {value}")