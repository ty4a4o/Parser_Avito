import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from config import USER_AGENTS, STOP_EXECUTION, RUN_MODE, SEARCH_QUERY

from avito_selectors import (
    search_input_selector,
    gallery_selector, left_btn_selector, right_btn_selector,
    btn_selector, popup_selector,
    title_selector, rec_selector, carousel_btn_selector
)

uc.Chrome.__del__ = lambda self: None
IS_HIDDEN = RUN_MODE == "hidden"

def setup_driver():
    options = uc.ChromeOptions()
    ua = random.choice(USER_AGENTS)
    screen_width, screen_height = random.choice([(1366, 768), (1536, 864), (1920, 1080)])

    options.add_argument(f"--window-size={screen_width},{screen_height}")
    options.add_argument("--window-position=0,0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")

    options.add_argument("--no-first-run")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-sync")
    options.add_argument("--dns-prefetch-disable")

    if IS_HIDDEN:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")

    options.page_load_strategy = 'eager'
    options.add_argument(f"--user-agent={ua}")
    driver = uc.Chrome(
        options=options,
        headless=IS_HIDDEN,
        use_subprocess=True,
    )

    if not IS_HIDDEN:
        try:
            driver.set_window_size(screen_width, screen_height)
            driver.set_window_position(0, 0)
        except Exception:
            pass

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
        }
    )

    return driver

#рандомное время
def idle_pause(min_sec=1.0, max_sec=3.0):
    time.sleep(random.uniform(min_sec, max_sec))

#случайные движения мышки
def ui_random_mouse_move(driver):
    if not check_browser(driver):
        return
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        actions = ActionChains(driver)
        actions.move_to_element(body)
        for _ in range(random.randint(1, 3)):
            actions.move_by_offset(random.randint(-80, 80), random.randint(-60, 60))
            actions.pause(random.uniform(0.08, 0.22))
        actions.perform()
    except Exception:
        pass

def ui_type_text(driver, element, text, min_delay=0.1, max_delay=0.15):
    if not check_browser(driver) or element is None:
        return False
    try:
        for ch in text:
            element.send_keys(ch)
            time.sleep(random.uniform(min_delay, max_delay))
            if random.random() < 0.1:
                time.sleep(random.uniform(0.18, 0.45))
        return True
    except Exception:
        return False

def ui_click(driver, element):
    if not check_browser(driver) or element is None:
        return False
    try:
        actions = ActionChains(driver)
        actions.move_to_element(element)
        actions.pause(random.uniform(0.10, 0.28))
        actions.move_by_offset(random.randint(-6, 6), random.randint(-6, 6))
        actions.pause(random.uniform(0.08, 0.20))
        actions.click()
        actions.perform()
        return True
    except Exception:
        return False

def ui_press_escape(driver):
    if not check_browser(driver):
        return False
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ESCAPE)
        return True
    except Exception:
        return False


def human_like_scroll(driver, element=None, target_y=None, max_distance=3000):

    viewport_height = driver.execute_script("return window.innerHeight;")
    page_height = driver.execute_script("return document.body.scrollHeight;")
    current_y = driver.execute_script("return window.pageYOffset;")

    if element is not None:
        rect = driver.execute_script(
            """
            const r = arguments[0].getBoundingClientRect();
            return { top: r.top, height: r.height };
            """,
            element
        )

        element_top_in_page = current_y + rect["top"]
        element_bottom_in_page = element_top_in_page + rect["height"]

        if rect["top"] < 0:
            # Элемент выше видимой области - скроллим вверх
            target_ratio = random.uniform(0.1, 0.3)  # Ближе к верху
            target_y = element_top_in_page - viewport_height * target_ratio
        elif rect["top"] + rect["height"] > viewport_height:
            # Элемент ниже видимой области - скроллим вниз
            target_ratio = random.uniform(0.65, 0.85)  # Ближе к низу
            target_y = element_top_in_page - viewport_height * target_ratio
        else:
            # Элемент уже виден, но не в центре
            target_ratio = random.uniform(0.4, 0.6)
            target_y = element_top_in_page - viewport_height * target_ratio

    elif target_y is None:
        target_y = random.randint(
            int(max_distance * 0.65),
            int(max_distance * 0.9)
        )
    target_y = max(0, min(target_y, page_height))

    distance = target_y - current_y
    distance = abs(distance)

    if distance < 30:
        return


    steps = random.randint(30, 45)

    for i in range(steps):
        if not check_browser(driver):
            return

        current_y = driver.execute_script("return window.pageYOffset;")
        remaining = target_y - current_y

        if abs(remaining) < 20:
            break

        direction = 1 if remaining > 0 else -1
        remaining_abs = abs(remaining)

        # плавное уменьшение шага ближе к цели
        base = max(10, remaining_abs // max(1, (steps - i)))
        step = random.randint(max(1, base // 2), base)

        driver.execute_script("window.scrollBy(0, arguments[0]);", direction * step)
        idle_pause(0.05, 0.25)

def basic_search(driver, query: str) -> bool:
    if not query or not check_browser(driver):
        return False

    try:
        print("Открываю avito.ru...")
        driver.get("https://www.avito.ru/")
        idle_pause(3.0, 6.0)

        # Поле поиска на главной
        search_input = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, search_input_selector))
        )

        try:
            ui_click(driver, search_input)
        except Exception:
            try:
                search_input.click()
            except Exception:
                pass

        idle_pause(0.2, 0.6)

        try:
            search_input.clear()
        except Exception:
            try:
                search_input.send_keys(Keys.CONTROL, "a")
                search_input.send_keys(Keys.BACKSPACE)
            except Exception:
                pass

        try:
            ui_type_text(driver, search_input, query)
        except Exception:
            return False

        idle_pause(2.1, 3.1)

        old_url = driver.current_url
        search_input.send_keys(Keys.ENTER)

        try:
            WebDriverWait(driver, 12).until(lambda d: d.current_url != old_url)
        except Exception:
            pass

        idle_pause(2.0, 4.0)

        for _ in range(2):
            if not check_browser(driver):
                return False
            human_like_scroll(driver)
            idle_pause(1.2, 3.2)

        return True

    except Exception as e:
        print(f"Ошибка при стартовом поиске: {str(e)[:150]}...")
        return False


def browse_photos(driver):
    try:
        print("Просмотр фотографий...")

        gallery_selector = "[data-marker='image-frame/image-wrapper']"

        gallery = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, gallery_selector))
        )

        human_like_scroll(driver, element=gallery)
        idle_pause(1.0, 1.5)

        ui_random_mouse_move(driver)

        if not ui_click(driver, gallery):
            print("Не смог открыть галерею.")
            return False
        print('Галерея открыта')
        idle_pause(1.5, 2.0)

        left_btn_selector =  "[data-marker='extended-gallery-frame/control-left']"
        right_btn_selector = "[data-marker='extended-gallery-frame/control-right']"

        left_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, left_btn_selector))
        )

        right_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, right_btn_selector))
        )

        photos_to_view = random.randint(2, 7)

        for i in range(photos_to_view):
            if not check_browser(driver):
                return
            btn = left_btn if random.random() > 0.77 else right_btn
            ui_click(driver, btn)
            idle_pause(1.0, 4.5)

        ui_press_escape(driver)
        idle_pause(1.5, 2.0)

        print(f"Просмотрено {photos_to_view} фотографий")
        return True

    except Exception as e:
        print(f"Ошибка просмотра фото: {str(e)[:100]}...")
        return False

def browse_reviews(driver, min_scrolls=7, max_scrolls=10) -> bool:
    if not check_browser(driver):
        return False

    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, btn_selector))
        )

        human_like_scroll(driver, element=btn)
        idle_pause(0.4, 0.9)

        if not ui_click(driver, btn):
            btn.click()

        idle_pause(0.8, 1.6)

        popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, popup_selector))
        )

        scrolls = random.randint(min_scrolls, max_scrolls)
        for _ in range(scrolls):
            if not check_browser(driver):
                return False

            delta = random.randint(100, 150)
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[1];",
                popup,
                delta
            )
            idle_pause(0.8, 1.5)

        ui_press_escape(driver)
        idle_pause(0.8, 1.6)

        return True

    except Exception as e:
        print(f"Ошибка при просмотре отзывов: {str(e)[:150]}...")
        return False

def click_show_more_recommendations(driver, times=3, pause_after_click=(2.2, 3.2)):
    clicks = 0

    carousel_buttons = driver.find_elements(By.CSS_SELECTOR, carousel_btn_selector)
    if carousel_buttons:
        print("Обнаружен i2i-carousel: работаю через scroll-button-forward.")

        if not check_browser(driver):
            return False

        btns = driver.find_elements(By.CSS_SELECTOR, carousel_btn_selector)
        if not btns:
            return False

        btn = btns[0]

        human_like_scroll(driver, element=btn)
        idle_pause(0.25, 0.6)
        ui_random_mouse_move(driver)

        if not ui_click(driver, btn):
            print("Не удалось кликнуть carousel forward.")
            return False

        clicks += 1
        idle_pause(0.35, 0.9)

        return True

    def is_interactable(el):
        try:
            if not el.is_displayed():
                return False
            if el.get_attribute("disabled") is not None:
                return False
            r = driver.execute_script(
                "const r=arguments[0].getBoundingClientRect(); return {w:r.width,h:r.height};",
                el
            )
            return (r["w"] or 0) > 5 and (r["h"] or 0) > 5
        except Exception:
            return False

    def reveal_block():
        try:
            title = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, title_selector))
            )
            human_like_scroll(driver, element=title)
            idle_pause(0.35, 0.85)
            ui_random_mouse_move(driver)

            if not ui_click(driver, title):
                return False

            idle_pause(0.8, 1.6)
            return True
        except Exception:
            return False

    revealed = False

    while clicks < times:
        if not check_browser(driver):
            break

        # Ищем кнопку "Показать ещё"
        try:
            btn = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, rec_selector))
            )
        except Exception:
            btn = None

        # Если кнопки нет, пытаемся раскрыть блок
        if btn is None:
            if not revealed:
                if not reveal_block():
                    print("Не удалось раскрыть блок рекомендаций.")
                    break
                idle_pause(1.0, 1.5)
                revealed = True
                continue

        # Проверяем, интерактивна ли кнопка
        if not is_interactable(btn):
            human_like_scroll(driver, element=btn)
            idle_pause(0.6, 1.0)

            try:
                btn = driver.find_element(By.CSS_SELECTOR, rec_selector)
            except Exception:
                btn = None

            if not is_interactable(btn):
                if not revealed:
                    if not reveal_block():
                        print("Кнопка 'Показать ещё' не интерактивна.")
                        break
                    revealed = True
                    continue

        # Кликаем по кнопке
        try:
            human_like_scroll(driver, element=btn)
            idle_pause(0.3, 0.7)

            if ui_click(driver, btn):
                clicks += 1
                print(f"Нажал 'Показать ещё' ({clicks}/{times})")
                idle_pause(*pause_after_click)
                ui_random_mouse_move(driver)
            else:
                print("Клик по 'Показать ещё' не сработал.")
                break

        except StaleElementReferenceException:
            idle_pause(0.6, 1.2)
            continue
        except Exception as e:
            print(f"Ошибка при клике: {str(e)[:100]}...")
            break

    return clicks > 0

#выполнение действий в случайном порядке
def run_random_session(driver):

    if not check_browser(driver):
        return False

    def micro_pause():
        ui_random_mouse_move(driver)
        idle_pause(1.1, 1.4)

    def do_random_scroll():
        for _ in range(random.randint(1, 3)):
            human_like_scroll(driver)

    def do_gallery():
        browse_photos(driver)

    def do_recommendations():
        click_show_more_recommendations(
            driver,
            times=random.randint(2, 4),
            pause_after_click=(1.0, 2.2),
        )

    def do_rewiews():
        browse_reviews(driver)

    #список возможных действий
    actions = [
        ("gallery", do_gallery),
        ("scroll", do_random_scroll),
        ("recom", do_recommendations),
        ("rewiews", do_rewiews)
    ]

    # Перемешиваем порядок
    random.shuffle(actions)

    print("Сценарий взаимодействий:", " -> ".join([name for name, _ in actions]))
    micro_pause()

    # Выполняем все
    for name, fn in actions:
        if not check_browser(driver):
            return False
        try:
            fn()
        except Exception as e:
            print(f"Действие '{name}' завершилось с ошибкой: {str(e)[:120]}...")
            micro_pause()
            continue
        micro_pause()
    return True

def check_browser(driver):
    global STOP_EXECUTION
    if STOP_EXECUTION:
        return False
    try:
        _ = driver.current_url
        return True
    except Exception:
        STOP_EXECUTION = True
        print("Браузер закрыт.")
        return False


def main():
    url = "https://www.avito.ru/ufa/telefony/iphone_13_128_gb_sim_esim_7805095808?context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6IngiO3M6MTY6Ijc5OE1qQ2dvdmgyZTk5aWIiO3390IQBJgAAAA"

    driver = None
    try:
        driver = setup_driver()
        basic_search(driver, SEARCH_QUERY)

        print("Открываю страницу объявления...")

        driver.get(url)
        idle_pause(10, 15)
        run_random_session(driver)

    except Exception as e:
        print(f"Ошибка: {str(e)[:200]}...")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        print("Работа завершена")


if __name__ == "__main__":
    main()