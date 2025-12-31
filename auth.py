import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AvitoAuthService:
    def __init__(self):
        self.options = Options()
        # self.options.add_argument("--headless") 
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # Отключаем логирование Chrome в консоль
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # Маскируемся под обычного пользователя
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    async def login_and_get_cookies(self, login, password):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_login, login, password)

    def _sync_login(self, login, password):
        driver = webdriver.Chrome(options=self.options)
        try:
            driver.get("https://www.avito.ru/profile/login")

            wait = WebDriverWait(driver, 15)
            login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))

            login_input.send_keys(login)
            driver.find_element(By.NAME, "password").send_keys(password)

            login_button = driver.find_element(By.XPATH, "//button[contains(.,'Войти')]")
            login_button.click()

            # --- БЛОК ОБРАБОТКИ КОДА ПОДТВЕРЖДЕНИЯ ---
            time.sleep(3) # Даем странице подумать

            # Проверяем, появилось ли поле для кода (селектор может меняться, обычно это input с определенным name)
            try:
                # Пытаемся найти поле ввода кода (например, по тегу input или атрибуту type="tel")
                code_field = driver.find_elements(By.CSS_SELECTOR, "input[data-marker='secondary-auth-code/input']")

                if code_field:
                    print("\n" + "="*30)
                    print("AVITO ЗАПРОСИЛ КОД ПОДТВЕРЖДЕНИЯ!")
                    sms_code = input("Введите код из SMS/Push прямо здесь в консоли: ")
                    print("="*30 + "\n")

                    code_field[0].send_keys(sms_code)

                    # Нажимаем кнопку подтверждения
                    confirm_button = driver.find_element(By.XPATH, "//button[@type='submit' or contains(.,'Подтвердить')]")
                    confirm_button.click()
            except Exception as e:
                print(f"Окно ввода кода не найдено или произошла ошибка: {e}")
            # -----------------------------------------

            # Ждем успешного входа
            wait.until(EC.url_to_be("https://www.avito.ru/"))

            cookies = driver.get_cookies()
            return {"status": "success", "cookies": cookies}

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            driver.quit()