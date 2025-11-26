import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Настройки
def random_delay(min_delay=1, max_delay=3): # Рандом задержка
    delay = random.uniform(min_delay, max_delay)
    print(f"Задержка: {delay:.2f} сек")
    time.sleep(delay)

def try_find_element(driver, locators, by=By.XPATH, timeout=10): # Поиск элемента
    for locator in locators:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return element
        except (NoSuchElementException, TimeoutException):
            continue
    return None

def setup_browser(): # Настройки браузера
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    return driver

def check_for_access_error(driver): # Поиск ошибки
    try:
        error_text_locators = [
            '//h2[contains(text(), "Доступ ограничен")]',
            '//div[contains(text(), "подтвердите, что вы не робот")]'
        ]
        error_element = try_find_element(driver, error_text_locators, timeout=5)
        if error_element:
            print("\n⛔️ Обнаружена ошибка доступа или капча")
            print("Введите капчу и нажмите Enter, чтобы продолжить...")
            input()
            return True
    except Exception:
        pass
    return False

def wait_for_page_content(driver, timeout=25): # Ожидание основного контента
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//h1[@data-marker="item-view/title-info"]'))
        )
        print("✅ Основное содержимое страницы загружено.")
        return True
    except TimeoutException:
        print("❌ Ключевой контент (заголовок) не найден за указанное время.")
        return False

def parse_additional_info(driver, data): #  Поиск кнопок
    
    # Показать телефон
    try:
        phone_button_locators = ['//button[@data-marker="item-phone-button/card"]']
        data["show_phone_number"] = "Доступно" if try_find_element(driver, phone_button_locators, timeout=2) else "Не найдено"
    except Exception:
        data["show_phone_number"] = "Не найдено"
        
    # Написать
    try:
        message_button_locators = [
            '//button[@data-marker="item-contact-buttons/send-message"]', # Чаще всего используется
            '//button[contains(text(), "Написать")]',
            '//a[@data-marker="messenger-button/link"]' # Ваш вариант (менее надежен)
        ]
        data["write_message"] = "Доступно" if try_find_element(driver, message_button_locators, timeout=2) else "Не найдено"
    except Exception:
        data["write_message"] = "Не найдено"

    # Все характеристики
    try:
        all_chars_locators = [
            '//div[contains(@class, "params-list-item")]/..//button[contains(text(), "Все характеристики")]', 
            '//a[@data-marker="item-specification-button"]'
        ]
        data["all_characteristics"] = "Доступно" if try_find_element(driver, all_chars_locators, timeout=3) else "Не найдено"
    except Exception:
        data["all_characteristics"] = "Не найдено"
        
    # Узнать подробности
    try:
        location_details_locators = [
            '//div[@data-marker="item-view/location"]//div[contains(text(), "узнать подробности")]',
            '//button[contains(text(), "узнать подробности")]'
        ]
        data["location_details"] = "Доступно" if try_find_element(driver, location_details_locators, timeout=3) else "Не найдено"
    except Exception:
        data["location_details"] = "Не найдено"

    # Показать карту
    try:
        map_link_locators = [
            '//div[@data-marker="item-map-button"]//div[contains(text(), "Показать карту")]',
            '//div[@data-marker="item-view/map"]',
            '//button[contains(text(), "Показать карту")]'
        ]
        data["show_map"] = "Доступно" if try_find_element(driver, map_link_locators, timeout=3) else "Не найдено"
    except Exception:
        data["show_map"] = "Не найдено"
        
    # Подробнее
    try:
        read_more_locators = [
            '//span[contains(text(), "Подробнее")]', 
            '//button[contains(text(), "Подробнее")]'
        ]
        data["read_more"] = "Доступно" if try_find_element(driver, read_more_locators, timeout=3) else "Не найдено"
    except Exception:
        data["read_more"] = "Не найдено"
        
    # Все опции
    try:
        all_options_locators = [
            '//button[contains(text(), "Все опции")]',
            '//button[@class="style__advanced-params-show-more___XzA5ZD"]'
        ]
        data["all_options"] = "Доступно" if try_find_element(driver, all_options_locators, timeout=3) else "Не найдено"
    except Exception:
        data["all_options"] = "Не найдено"

    # Показать еще объявления
    try:
        similar_items_locators = [
            '//button[contains(text(), "Показать еще объявления")]',
            '//a[contains(text(), "Показать еще объявления")]',
            '//a[@data-marker="related-items/show-more-button"]',
            '//a[@data-marker="similar-items/show-more-button"]'
        ]
        data["show_more_ads"] = "Доступно" if try_find_element(driver, similar_items_locators, timeout=3) else "Не найдено"
    except Exception:
        data["show_more_ads"] = "Не найдено"
    
    return data

def parse_avito_page(url): # Парсинг
    driver = None
    try:
        driver = setup_browser()
        print(f"Переходим по ссылке: {url}")
        driver.get(url)

        if check_for_access_error(driver):
            print("Проблема решена вручную, перезагружаем страницу...")
            driver.get(url)
            random_delay()

        if not wait_for_page_content(driver):
            return {"error": "Страница не загрузила ключевой контент."}

        data = {}

        # Заголовок
        title_locators = ['//h1[@data-marker="item-view/title-info"]']
        title_elem = try_find_element(driver, title_locators)
        data["title"] = title_elem.text if title_elem else "Не найдено"

        # Цена
        price_locators = ['//span[@class="FfCOp"]']
        price_elem = try_find_element(driver, price_locators, timeout=5)
        if price_elem:
            price_text = "".join(filter(str.isdigit, price_elem.text))
            data["price"] = price_text
        else:
            data["price"] = "Не найдено"

        # Описание
        description_locators = ['//div[@data-marker="item-view/item-description"]']
        description_elem = try_find_element(driver, description_locators)
        data["description"] = description_elem.text.strip() if description_elem else "Не найдено"

        # Фото
        try:
            js_script = 'return Array.from(document.querySelectorAll(\'div[data-marker="item-view/gallery"] img\')).map(img => img.src);'
            photo_urls = driver.execute_script(js_script)
            data["photos"] = photo_urls if photo_urls else ["Фото не найдены"]
        except Exception as e:
            print(f"❌ Не удалось получить фото через JS: {e}")
            data["photos"] = ["Фото не найдены"]

        # Новые данные
        data = parse_additional_info(driver, data)

        return data
    
    except Exception as e:
        print(f"❌ Произошла ошибка в процессе парсинга: {e}")
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()
            print("\nБраузер закрыт.")

if __name__ == "__main__":
    target_url = "https://www.avito.ru/ufa/telefony/iphone_14_pro_max_512_gb_esim_7770504833"
    result = parse_avito_page(target_url)

    print("\n" + "="*40 + " Результат парсинга " + "="*40)
    if "error" in result:
        print(f"Ошибка: {result['error']}")
    else:
        for key, value in result.items():
            if key == "photos":
                print(f"Фото: ({len(value)} шт.)")
                for i, photo_url in enumerate(value, 1):
                    print(f"   {i}. {photo_url}")

                print("\n" + "="*40 + " Результат парсинга " + "="*40)

            # Статус кнопок
            elif key in ["show_phone_number", "write_message", "all_characteristics", "location_details", "show_map", "read_more", "all_options", "show_more_ads"]:
                
                status_emoji = "✅" if value == "Доступно" else "❌"
                print(f"{status_emoji} '{key.replace('_', ' ').title()}': {value}")
            # Игнорируем старых ключей
            elif key in ["add_to_cart", "buy_with_delivery"]:
                continue
            else:
                print(f"{key.capitalize()}: {value}")
                
    print("="*100)
