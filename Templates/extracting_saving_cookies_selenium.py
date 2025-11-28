import time
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def make_driver():
    opts = Options()
    # add any common options you like here
    return uc.Chrome(options=opts)

def save_cookies(start_url: str, cookie_file: str = "cookies.pkl"):
    """Open start_url, let user log in manually, then save cookies."""
    driver = make_driver()
    driver.get(start_url)
    print(f"Opened {start_url}")
    print("Log in or set up the session in the browser window.")
    input("When finished, press Enter here to save cookies... ")

    cookies = driver.get_cookies()
    pickle.dump(cookies, open(cookie_file, "wb"))
    print(f"Saved {len(cookies)} cookies to {cookie_file}")

    driver.quit()

def load_cookies(base_url: str, cookie_file: str = "cookies.pkl", domain_override: str | None = None):
    """Load cookies from cookie_file into a new browser for base_url."""
    driver = make_driver()
    driver.get(base_url)
    time.sleep(2)

    cookies = pickle.load(open(cookie_file, "rb"))
    added = 0
    for cookie in cookies:
        if domain_override is not None:
            cookie["domain"] = domain_override

        # Remove keys Selenium may not like
        cookie.pop("sameSite", None)
        try:
            driver.add_cookie(cookie)
            added += 1
        except Exception:
            pass

    print(f"Added {added} cookies from {cookie_file}")
    driver.get(base_url)
    return driver

if __name__ == "__main__":
    mode = input("Type 'save' to save cookies or 'load' to load cookies: ").strip().lower()

    if mode == "save":
        url = input("Enter URL to open and log in (e.g. https://github.com/login): ").strip()
        file_name = input("Cookie file name (default cookies.pkl): ").strip() or "cookies.pkl"
        save_cookies(url, file_name)

    elif mode == "load":
        base_url = input("Enter base URL to use cookies on (e.g. https://github.com): ").strip()
        file_name = input("Cookie file name (default cookies.pkl): ").strip() or "cookies.pkl"
        domain_override = input("Domain override (blank for none, e.g. .example.com): ").strip() or None

        driver = load_cookies(base_url, file_name, domain_override)
        print("Session loaded; keep the browser open to inspect it.")

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            driver.quit()
    else:
        print("Unknown mode. Use 'save' or 'load'.")
