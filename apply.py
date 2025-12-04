import time

def apply_jobs(driver, job_links, limit):
    applied = 0
    for link in job_links:
        if applied >= limit:
            break
        
        driver.get(link)
        time.sleep(3)

        try:
            apply_btn = driver.find_element("xpath", "//*[contains(text(),'Apply')]")
            apply_btn.click()
            applied += 1
            print("📤 Applied:", link)
        except:
            print("⏭️ Skipped:", link)

    return applied
