from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login(driver, email, password):
    driver.get("https://www.naukri.com/nlogin/login")

    wait = WebDriverWait(driver, 30)

    # 🔹 Close popup if appears
    try:
        popup_close = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='login_Layer']//span"))
        )
        popup_close.click()
        print("🪟 Popup closed")
        time.sleep(1)
    except:
        print("ℹ️ No popup")

    # 🔹 Enter email
    wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(email)

    # 🔹 Enter password
    driver.find_element(By.ID, "passwordField").send_keys(password)

    # 🔹 Click login
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # 🔹 Wait for successful redirect
    try:
        wait.until(EC.url_contains("dashboard"))
        print("🔐 Login success (Dashboard loaded)")
    except:
        print("⚠️ Login clicked but dashboard not arrived")

    return driver
