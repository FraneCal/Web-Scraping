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

# Wait for the page to load
time.sleep(4)

# Accepting cookies (if they appear)
try:
    def get_shadow_root(element):
        return driver.execute_script('return arguments[0].shadowRoot', element)

    shadow_host = driver.find_element(By.ID, 'usercentrics-root')
    button = get_shadow_root(shadow_host).find_element(By.CSS_SELECTOR, '[data-testid=uc-accept-all-button]')
    button.click()
except:
    print("Accept cookies not found.")


# City name
city_inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="oss-location"]')))
city_input = [element for element in city_inputs if element.is_displayed()][0]
city_input.click()
city_input.send_keys(input('Enter the city name you want to search for: '))
time.sleep(1)
city_input.send_keys(Keys.ENTER)

# Buying, renting or building
while True:
    buying_or_renting_inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="oss-form"]/article/div/div[1]/div/div[3]/div/div/select')))
    buying_or_renting_input = [element for element in buying_or_renting_inputs if element.is_displayed()][0]
    options = int(input('Enter the number of one of the options: 0-Rent, 1-Buying, 2-Building: '))
    if options < 0 or options > 2:
        options = int(input('Enter the number of one of the options: 0-Rent, 1-Buying, 2-Building: '))
    else:
        select_buy_or_rent = Select(buying_or_renting_input).select_by_index(options)
        break

# Apartmanent or house
apart_or_house = Select(driver.find_element(By.NAME, 'oss-rent')).select_by_index(2)

# Search for the results
search_button = driver.find_element(By.XPATH, '//*[@id="oss-form"]/article/div/div[3]/button')
search_button.click()

# Handle captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

# Wait for the resutls to load
time.sleep(5)

page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, "html.parser")
