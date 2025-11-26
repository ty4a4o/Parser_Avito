from selenium import webdriver
from selenium_stealth import stealth
import time

def init_webdriver():
    driver = webdriver.Chrome()
    stealth(driver,
            languages=["en_US", "en"],
            vendor="Google Inc.",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            platform="win35")
    return driver

driver = init_webdriver()
driver.get("https://www.avito.ru/ufa/avtomobili/ford_focus_1.6_amt_2011_175_488_km_7392369082?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJsb3VITEhoTVVlMm5vOVdjIjt9pzQRAz8AAAA")
time.sleep(10)