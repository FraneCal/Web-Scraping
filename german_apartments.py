from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://www.immobilienscout24.de/"

driver = webdriver.Chrome()
driver.get(URL)

time.sleep(3)

def get_shadow_root(element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

shadow_host = driver.find_element(By.ID, 'usercentrics-root')
button = get_shadow_root(shadow_host).find_element(By.CSS_SELECTOR, '[data-testid=uc-accept-all-button]')
button.click()

time.sleep(2)

city = driver.find_element(By.CLASS_NAME, 'grid-item oss-location-container absolute-reference oss-layer-one-whole lap-four-fifths desk-four-fifths')
driver.execute_script("arguments[0].click();", city)
city.send_keys('Berlin')

page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, "html.parser")
