import os, json, gzip, base64, time

def login_with_cookies(driver):
    print("🔐 Logging using encoded cookies...")

    encoded = os.environ.get("NAUKRI_COOKIES_B64")
    compressed = base64.b64decode(encoded)
    cookies = json.loads(gzip.decompress(compressed))

    driver.get("https://www.naukri.com/")
    time.sleep(2)
    driver.delete_all_cookies()

    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)

    driver.get("https://www.naukri.com/mnjuser/homepage")
    time.sleep(3)

    if "homepage" in driver.current_url.lower():
        print("🎯 Cookie login success!")
        return driver

    raise Exception("❌ Cookie login failed — Refresh cookies manually")
