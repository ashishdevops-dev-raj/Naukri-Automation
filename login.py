from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login(driver, email, password):
    wait = WebDriverWait(driver, 30)

    # Force login URL
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(3)

    print("🔍 Checking which login screen is loaded ...")

    # Try login screen type 1
    try:
        username = wait.until(
            EC.visibility_of_element_located((By.ID, "usernameField"))
        )
        print("📌 Using old login page UI")

        username.clear()
        username.send_keys(email)

        driver.find_element(By.ID, "passwordField").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

    except:
        # Try login screen type 2
        try:
            print("📌 Using new login page UI")
            email_box = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']"))
            )
            email_box.clear()
            email_box.send_keys(email)

            driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
            time.sleep(2)

            # Add password on new UI
            wait.until(
                EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
            ).send_keys(password)

            driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

        except:
            raise Exception("❌ Unable to find ANY login form. Page redirected!")

    # Wait for redirect → Dashboard/Home/Profile
    try:
        wait.until(
            EC.any_of(
                EC.url_contains("dashboard"),
                EC.url_contains("profile"),
                EC.url_contains("naukri"),
            )
        )
        print("🔐 Login Successful!")
    except:
        print("⚠️ Login clicked, maybe OTP required?")

    return driver
