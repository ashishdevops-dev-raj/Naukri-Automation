import pickle
import base64
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.naukri.com/nlogin/login")
print("⭐ Login manually… DO NOT CLOSE BROWSER")
time.sleep(40)  # Login manually

cookies = driver.get_cookies()
driver.quit()

cookies_json = json.dumps(cookies)
cookies_b64 = base64.b64encode(cookies_json.encode()).decode()

with open("cookies_b64.txt", "w") as f:
    f.write(cookies_b64)

print("\n✅ Cookies saved successfully!")
print("📄 Copy the value from cookies_b64.txt and add it to GitHub Secrets.")
