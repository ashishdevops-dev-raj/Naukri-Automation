from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver, email, password):
    driver.get("https://www.naukri.com/nlogin/login")
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "usernameField"))
    ).send_keys(email)

    driver.find_element(By.ID, "passwordField").send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Login']").click()

    WebDriverWait(driver, 20).until(
        EC.url_contains("profile")
    )
    print("🔐 Login Success")
    return driver
