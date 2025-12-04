from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login(driver, email, password):
    wait = WebDriverWait(driver, 30)

    # Force correct login URL to avoid redirect
    driver.get("https://www.naukri.com/nlogin/login")

    # Make sure page is fully loaded
    time.sleep(3)

    # Close popup if shows
    try:
        popup = driver.find_element(By.XPATH, "//span[@class='crossIcon chatBot chatBot-ico']")
        popup.click()
        print("🪟 Popup closed")
    except:
        print("ℹ️ No popup found")

    # Retry clicking Username field if not visible the first time
    for i in range(3):
        try:
            username = wait.until(
                EC.visibility_of_element_located((By.ID, "usernameField"))
            )
            username.clear()
            username.send_keys(email)
            break
        except:
            print(f"Retrying username field attempt {i+1}")
            driver.get("https://www.naukri.com/nlogin/login")
            time.sleep(2)
    else:
        raise Exception("❌ usernameField not found!!")

    # Enter password
    wait.until(
        EC.visibility_of_element_located((By.ID, "passwordField"))
    ).send_keys(password)

    # Click Login button
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait till redirect → Dashboard / Homepage
    try:
        wait.until(
            EC.any_of(
                EC.url_contains("dashboard"),
                EC.url_contains("profile"),
                EC.url_contains("nsmart"),
            )
        )
        print("🔐 Login Successful!")
    except:
        print("⚠️ Login button clicked but redirect not confirmed yet")

    return driver
