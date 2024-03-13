# COMPLETE SPECIAL OFFER FUNCTION
# COMPLETE EXTRACTING INFORMATION SO IT SCRAPES ONLY m2 WHICH YOU NEED

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import random
import time
import pandas as pd

def solve_captcha_slider(driver):
    try:
        slider = driver.find_element(By.CLASS_NAME, 'geetest_slider_button')
        for x in range(0, 200, 10):
            actions.move_to_element(slider).click_and_hold().move_by_offset(x, 0).release().perform()
            time.sleep(0.5)
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

house_data = {
        'House link': [],
        'Price per square meter [€]': [],
    } 


def special_offer_container(soup):
    # Looking for special offer container
    try:
        for _ in range(2):
            # Show all of the offers in the special offer container
            show_more_units = driver.find_element(By.CLASS_NAME, 'padding-left-none link-text-secondary button')
            show_more_units.click()

        time.sleep(1)
        containers = soup.find_all('div', class_='grid grid-flex grid-justify-space-between')
        links_container = [container.find('a')['href'] for container in containers]
        for link_container, info_container in zip(links_container, containers):
            house_link_container = f"https://www.immobilienscout24.de{link_container}"

            text_container = info_container.getText().strip()
            print(text_container)
            try:
                if '€' in text_container:
                    # Remove euro sign and convert to int
                    price = int(text_container.replace('€', '').replace('.', '').replace(',', '').strip())
                    print(price)
                elif 'm²' in text_container:
                    # Remove square meter sign and convert to int
                    square_meter_str = text_container.replace('m²', '').replace(',', '').strip()
                    print(square_meter_str)

                    # Handle cases where dot is used as a thousand separator
                    if '.' in square_meter_str and square_meter_str.count('.') == 1:
                        # If there is only one dot, consider it as a thousand separator
                        square_meter_str = square_meter_str.replace('.', '')
                    elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                        # If there are multiple dots, keep only the last one as the decimal point
                        square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace('.', '')

                    # Convert to float, handle the case when it's zero
                    square_meter = float(square_meter_str) if square_meter_str else 0.0

                    # Check if square_meter is non-zero before division
                    if square_meter != 0:
                        price_per_square_meter = price / square_meter

                        # Check if price_per_square_meter is within the specified range
                        if 2000 <= price_per_square_meter <= 3000:
                            # Append data to the list for saving to Excel
                            house_data['House link'].append(house_link_container)
                            house_data['Price per square meter [€]'].append(price_per_square_meter)
            except:
                print("Special offer price or the living space information is missing.")
    
    except:
        print('No special offers found.')

    return house_data


def extract_information(soup):
    # Finding and extracting the regular information   

    information = soup.find_all('dd', class_='font-highlight font-tabular')
    links = [info.find_previous('div', class_='grid-item').find('a')['href'] for info in information]

    for link, info in zip(links, information):
        house_link = f"https://www.immobilienscout24.de{link}"

        # Extract and print only the prices and square meters
        text = info.getText().strip()
        try:
            if '€' in text:
                # Remove euro sign and convert to int
                price = int(text.replace('€', '').replace('.', '').replace(',', '').strip())
            elif 'm²' in text:
                # Remove square meter sign and convert to int
                square_meter_str = text.replace('m²', '').replace(',', '').strip()
                #print(square_meter_str)

                # Handle cases where dot is used as a thousand separator
                if '.' in square_meter_str and square_meter_str.count('.') == 1:
                    # If there is only one dot, consider it as a thousand separator
                    square_meter_str = square_meter_str.replace('.', '')
                elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                    # If there are multiple dots, keep only the last one as the decimal point
                    square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace('.', '')

                # Convert to float, handle the case when it's zero
                square_meter = float(square_meter_str) if square_meter_str else 0.0

                # Check if square_meter is non-zero before division
                if square_meter != 0:
                    price_per_square_meter = price / square_meter

                    # Check if price_per_square_meter is within the specified range
                    if 2000 <= price_per_square_meter <= 3000:
                        # Append data to the list for saving to Excel
                        house_data['House link'].append(house_link)
                        house_data['Price per square meter [€]'].append(price_per_square_meter)
        except:
            print("Price or the living space information is missing.")

    return house_data

# Set up the WebDriver
base_url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/haus-kaufen?enteredFrom=result_list'
start_page = 1
max_pages = 1

driver = webdriver.Chrome()
actions = ActionChains(driver)
driver.get(f'{base_url}?enteredFrom=result_list')

# Wait for the page to load
time.sleep(5)

# Click captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

# Solve captcha slider
solve_captcha_slider(driver)

time.sleep(3)

# Accept cookies
accept_cookies(driver)

current_page = start_page

while current_page <= max_pages:
    # Extract information from the current page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    results = extract_information(soup)
    special_offer_results = special_offer_container(soup)

    if results:
        # Save the all_results to the Excel file after each page if there are results
        df = pd.DataFrame(house_data)
        df.to_excel('houses_berlin.xlsx', index=False)

    # Move to the next page
    current_page += 1
    next_url = f'{base_url}?pagenumber={current_page}'
    driver.get(next_url)

    # Extract and print the current page number
    print(f"Scraping page number: {current_page}")

    # Add a delay to avoid being blocked by the website
    time.sleep(3)

# Quit the driver
driver.quit()
