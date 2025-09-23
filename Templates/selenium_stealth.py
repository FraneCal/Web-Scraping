#!/usr/bin/env python3
import random
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---------------- CONFIG (from you) ----------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0; IN) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 IN",
    "Mozilla/5.0 (Linux; Android 11; RMX2185) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-M315F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K7AI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 IN",
    "Mozilla/5.0 (Linux; Android 13; CPH2381) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; 2201116TI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
]

BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-crash-reporter',
    '--disable-logging',
    '--log-level=3',
    '--disable-hang-monitor',
    '--disable-client-side-phishing-detection',
    '--disable-component-update',
    '--start-maximized',
    "--blink-settings=imagesEnabled=false",
    '--disable-blink-features=AutomationControlled'
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://search.yahoo.com/",
    "https://duckduckgo.com/",
    "https://www.ecosia.org/",
    "https://www.startpage.com/",
    "https://www.qwant.com/",
    "https://www.aol.com/",
    "https://search.brave.com/",
]

STEALTH_JS = r'''
(() => {
    try {
        // Remove webdriver property
        try { delete Object.getPrototypeOf(navigator).webdriver; } catch(e) {}

        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {0: {type: 'application/x-google-chrome-pdf', description: 'Portable Document Format'}},
                {0: {type: 'application/pdf', description: 'Portable Document Format'}}
            ]
        });

        // Spoof platform (Android/Windows)
        Object.defineProperty(navigator, 'platform', {
            get: () => (/(Android|Linux)/.test(navigator.userAgent) ? 'Linux armv8l' : 'Win32')
        });

        // Spoof languages (India)
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-IN', 'en', 'hi-IN']
        });

        // Spoof connection
        Object.defineProperty(navigator, 'connection', {
            get: () => ({ downlink: 10, effectiveType: '4g', rtt: 100, saveData: false, type: 'wifi' })
        });

        // Spoof hardwareConcurrency / deviceMemory
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

        // Spoof chrome object
        window.chrome = window.chrome || {
            app: { isInstalled: false },
            webstore: { onInstallStageChanged: {}, onDownloadProgress: {} },
            runtime: {}
        };

        // Spoof permissions.query
        Object.defineProperty(navigator, 'permissions', {
            get: () => ({ query: (parameters) => (parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : Promise.resolve({ state: 'granted' })) })
        });

        // Spoof WebGL vendor/renderer via getParameter override
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            try {
                if (parameter === 37445) return 'ARM';
                if (parameter === 37446) return 'Mali-G57 MC2';
            } catch (e) {}
            return getParameter.call(this, parameter);
        };
    } catch (e) { /* ignore */ }
})();
'''

# ---------------- target ----------------
URL = "ADD YOUR URL HERE"

# --------------- setup & run ---------------
def main():
    # ensure chromedriver exists for current chrome
    chromedriver_autoinstaller.install()

    options = Options()

    # random user agent
    ua = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={ua}")

    # add browser args
    for a in BROWSER_ARGS:
        options.add_argument(a)

    # OPTIONAL: run headless if you don't want visible browser
    # options.add_argument("--headless=new")

    # create driver
    driver = webdriver.Chrome(options=options)

    # inject stealth JS so it runs before page scripts
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": STEALTH_JS})
    except Exception:
        # older selenium/chrome combos might fail; continue anyway
        pass

    # set extra headers (random referer + accept-language)
    headers = {
        "Referer": random.choice(REFERERS),
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
    except Exception:
        pass

    # open page, wait 5s, quit
    try:
        driver.get(URL)
        time.sleep(5)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
