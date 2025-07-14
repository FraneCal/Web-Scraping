#---------------------------------- STARTING TEMPLATE WHEN SCRAPING USING BEAUTIFUL SOUP AND SELENIUM (e.g. WHEN THE PAGE IS DYNAMIC) ----------------------------------#

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

URL = "ENTER URL"

driver = webdriver.Chrome()
driver.get(URL)

time.sleep(3)

# Click a button
try:
    some_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, 'ENTER XPATH HERE')))
    some_button.click()
except TimeoutException:
    print("No button found.")

page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, "html.parser")

# START SCRAPING :)
