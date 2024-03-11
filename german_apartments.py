from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import random
import time

def solve_captcha_slider(driver):
    try:
        slider = driver.find_element(By.CLASS_NAME, 'geetest_slider_button')
        attempt_counter = 0

        while attempt_counter < 6:
            actions.move_to_element(slider).click_and_hold().move_by_offset(10, 0).release().perform()
            time.sleep(0.1)

            # Check if puzzle captcha is still present
            if EC.presence_of_element_located((By.CLASS_NAME, 'geetest_radar_tip'))(driver):
                attempt_counter += 1
            else:
                break

    except:
        print('No slider found. Continuing with the code.')

def accept_cookies(driver):
    try:
        def get_shadow_root(element):
            return driver.execute_script('return arguments[0].shadowRoot', element)

        shadow_host = driver.find_element(By.ID, 'usercentrics-root')
        button = get_shadow_root(shadow_host).find_element(By.CSS_SELECTOR, '[data-testid=uc-accept-all-button]')
        button.click()
    except:
        print("Accept cookies not found.")

def extract_information(soup):
    # Find links inside the information div
    information = soup.find_all('dd', class_='font-highlight font-tabular')
    links = [info.find_previous('div', class_='grid-item').find('a')['href'] for info in information]

    for link, info in zip(links, information):
        house_link = f"https://www.immobilienscout24.de{link}"

        # Extract and print only the prices and square meters
        text = info.getText().strip()
        if '€' in text:
            # Remove euro sign and convert to int
            price = int(text.replace('€', '').replace('.', '').replace(',', '').strip())
        elif 'm²' in text:
            # Remove square meter sign and convert to int
            square_meter_str = text.replace('m²', '').replace(',', '').strip()

            # Handle cases where dot is used as a thousand separator
            if '.' in square_meter_str and square_meter_str.count('.') == 1:
                # If there is only one dot, consider it as a thousand separator
                square_meter_str = square_meter_str.replace('.', '')
            elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                # If there are multiple dots, keep only the last one as the decimal point
                square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace('.', '')

            square_meter = float(square_meter_str)

            # Calculate price per square meter
            price_per_square_meter = price / square_meter

            # Print the result for houses that meet the criteria
            if 2000 <= price_per_square_meter <= 3000:
                print(f'House Link: {house_link}')
                print(f'Price per square meter: {price_per_square_meter:.2f}')
                print('-' * 30)

# Set up the WebDriver
URL = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-kaufen?enteredFrom=result_list'

driver = webdriver.Chrome()
actions = ActionChains(driver)
driver.get(URL)

# Wait for the page to load
time.sleep(5)

# Click captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

time.sleep(5)
# Solve captcha slider
solve_captcha_slider(driver)

time.sleep(5)
# Accept cookies
accept_cookies(driver)

while True:
    # Extract information from the current page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    extract_information(soup)

    # Click on the next page if available, otherwise break out of the loop
    try:
        if "page" not in driver.current_url:
            next_page_xpath = '//*[@id="listings"]/div/ul/li[7]/a'
        elif "pagenumber=2" in driver.current_url:
            next_page_xpath = '//*[@id="listings"]/div/ul/li[8]/a'
        elif "pagenumber=3" in driver.current_url:
            next_page_xpath = '//*[@id="listings"]/div/ul/li[8]/a'
        else:
            next_page_xpath = '//*[@id="listings"]/div/ul/li[9]'

        # Extract and print the current page number
        current_page_number = driver.current_url.split("=")[-1]
        print(f"Scraping page number: {current_page_number}")

        next_page = driver.find_element(By.XPATH, next_page_xpath)
        next_page.click()
        time.sleep(5)
    except:
        print("No more pages to click. Exiting the loop.")
        break

# Quit the driver
driver.quit()
