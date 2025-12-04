from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import time

Naukri_URL = "https://www.naukri.com/nlogin/login"

def save_cookies():
    options = Options()
    options.add_experimental_option("detach", True)  # keeps browser open
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(Naukri_URL)
    print("\n👉 Please log in manually (enter OTP, solve CAPTCHA)\n")
    while "dashboard" not in driver.current_url.lower():
        time.sleep(2)

    print("\n🎉 Login success — saving cookies...\n")
    cookies = driver.get_cookies()
    with open("cookies_string.txt", "w") as f:
        f.write(str(cookies))

    print("📦 Cookies saved in cookies_string.txt")
    driver.quit()


if __name__ == "__main__":
    save_cookies()
