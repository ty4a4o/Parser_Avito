import time
import random
import undetected_chromedriver as uc
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.page_load_strategy = 'eager'
    driver = uc.Chrome(options=options)
    return driver


def human_like_mouse_move(x, y):
    for _ in range(random.randint(2, 4)):
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        pyautogui.moveTo(
            x + offset_x,
            y + offset_y,
            duration=random.uniform(0.2, 0.5),
            tween=pyautogui.easeInOutQuad
        )
        time.sleep(random.uniform(0.1, 0.3))
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()


def random_smooth_scroll(driver):
    for _ in range(random.randint(2, 5)):
        scroll_amount = random.choice([-1, 1]) * random.randint(300, 800)
        driver.execute_script(f"""
            window.scrollBy({{
                top: {scroll_amount},
                behavior: 'smooth'
            }});
        """)
        time.sleep(random.uniform(1.0, 2.0))


def browse_photos(driver):
    try:
        print("Просмотр фотографий...")

        gallery = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-marker='image-frame/image-wrapper']"))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", gallery)
        time.sleep(random.uniform(1.0, 1.5))

        location = gallery.location
        size = gallery.size
        click_x = location['x'] + size['width'] // 2 + random.randint(-10, 10)
        click_y = location['y'] + size['height'] // 2 + random.randint(-10, 10)

        human_like_mouse_move(click_x, click_y)
        time.sleep(random.uniform(1.5, 2.5))

        left_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-marker='extended-gallery-frame/control-left']"))
        )

        right_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-marker='extended-gallery-frame/control-right']"))
        )

        photos_to_view = random.randint(2, 7)
        size = left_btn.size
        for i in range(photos_to_view):
            btn = left_btn if random.random() > 0.77 else right_btn
            btn_loc = btn.location
            human_like_mouse_move(
                btn_loc['x'] + size['width'] // 2 + random.randint(-3, 3),
                btn_loc['y'] + + size['height'] // 2 + random.randint(-10, 10)
            )
            time.sleep(random.uniform(1.0, 1.8))

        pyautogui.press('esc')
        time.sleep(random.uniform(0.5, 1.2))

        print(f"Просмотрено {photos_to_view} фотографий")
        return True

    except Exception as e:
        print(f"Ошибка просмотра фото: {str(e)[:100]}...")
        return False


def main():
    url = "https://www.avito.ru/sterlitamak/telefony/iphone_16_128_gb_7625135542"

    driver = None
    try:
        driver = setup_driver()
        print("Открываю страницу...")
        driver.get(url)
        time.sleep(random.uniform(20.0,20.0))

        random_smooth_scroll(driver)

        browse_photos(driver)

    except Exception as e:
        print(f"Ошибка: {str(e)[:100]}...")
    finally:
        if driver:
            driver.quit()
        print("Работа завершена")


if __name__ == "__main__":
    main()