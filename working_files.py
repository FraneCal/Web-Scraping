from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import sqlite3

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

house_data = {
        'House link': [],
        'Price per square meter [€]': [],
    } 

def special_offer_container(soup):
    # Looking for special offer container
    while True:
        try:
            # Show all of the offers in the special offer container
            #show_more_units = driver.find_element(By.XPATH, '//*[@id="result-p-149403793"]/div[3]/button')
            show_more_units = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "weitere Einheiten anzeigen")]')))
            show_more_units.click()
            time.sleep(0.2)
            print('Show more units clicked.')

        except:
            print('All special offer units loaded.')
            break

    time.sleep(20)
    box = soup.find('article', class_='result-list-entry result-list-entry--xl type-project type-xl project-redesign')
    containers = box.find_all('div', class_='grid-item margin-right-m listing-details')
    links_container = [container.find('a')['href'] for container in containers]
    for link_container, info_container in zip(links_container, containers):
        house_link_container = f"https://www.immobilienscout24.de{link_container}"
        
        prices = soup.find('span', class_='font-highlight font-line-s').getText().strip()
        #print(prices)

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
                    price_per_square_meter = round(price / square_meter, 2)
                    print(f'Price per square meter: {price_per_square_meter}')

                    # Check if price_per_square_meter is within the specified range
                    if 2000 <= price_per_square_meter <= 3000:
                        # Append data to the list for saving to Excel
                        house_data['House link'].append(house_link_container)
                        house_data['Price per square meter [€]'].append(price_per_square_meter)
        except:
            print("Special offer price or the living space information is missing.")

    return house_data


def extract_information(soup):
    # Find all containers
    containers = soup.find_all('div', class_='grid grid-flex grid-align-center grid-justify-space-between')

    # Iterate over containers
    for container in containers:
        # Find all dd elements within the container
        informations = container.find_all('dd')

        # Extract links from a elements within the container
        links = container.find_all('a')
        links_list = [f"https://www.immobilienscout24.de{link.get('href')}" for link in links]

        # Extract text from dd elements
        variable = [information.getText() for information in informations]

        # Extract price and square meter information from the correct positions
        for i in range(0, len(variable), 2):
            # Check if there are enough elements in the variable list
            if i + 1 < len(variable):
                price_text = variable[i]
                square_meter_text = variable[i + 1]

                # Check if both price and square meter information are present
                if price_text and square_meter_text:
                    try:
                        # Remove euro sign and convert price to int
                        price = int(price_text.replace('€', '').replace('.', '').replace(',', '').strip())

                        # Remove square meter sign and convert to float
                        square_meter_str = square_meter_text.replace('m²', '').replace(',', '').strip()

                        # Handle cases where dot is used as a thousand separator
                        if '.' in square_meter_str and square_meter_str.count('.') == 1:
                            # If there is only one dot, consider it as a thousand separator
                            square_meter_str = square_meter_str.replace('.', '')
                        elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                            # If there are multiple dots, keep only the last one as the decimal point
                            square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace(
                                '.', '')

                        # Convert square meter to float
                        square_meter = float(square_meter_str)

                        # Check if square_meter is non-zero before division
                        if square_meter != 0:
                            price_per_square_meter = round(price / square_meter, 2)

                            # Check if price_per_square_meter is within the specified range
                            if 2000 <= price_per_square_meter <= 3000:
                                # Append data to the list for saving to Excel
                                house_data['House link'].extend(links_list)
                                house_data['Price per square meter [€]'].append(price_per_square_meter)
                    except (ValueError, IndexError):
                        print("Price or the living space information is missing or invalid.")

    return house_data
    

# Create SQLite connection and cursor
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS houses (
                    id INTEGER PRIMARY KEY,
                    house_link TEXT,
                    price_per_square_meter REAL
                )''')

# Set up the WebDriver
base_url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-kaufen'
start_page = 1

# Generate fake user agents
options = Options()
ua = UserAgent()
user_agent = ua.random

options.add_argument(f'--user-agent={user_agent}')

driver = webdriver.Chrome(options=options)
actions = ActionChains(driver)
driver.get(f'{base_url}?enteredFrom=result_list')

# Wait for the page to load
time.sleep(5)

# Click captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

time.sleep(3)

# Solve captcha slider
solve_captcha_slider(driver)

time.sleep(3)

# Accept cookies
accept_cookies(driver)

while True:
    # Extract information from the current page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # containers = soup.find_all('div', class_='grid grid-flex grid-align-center grid-justify-space-between')
    # for container in containers:
    # # Find all dd elements within the container
    #     informations = container.find_all('dd')
        
    #     # Extract text from dd elements
    #     variable = [information.getText() for information in informations]
        
    #     # Remove every 3rd and 4th element
    #     modified_list = variable[:2] + variable[4:]
        
    #     # Print modified list
    #     print(modified_list)
        
    special_offer_results = special_offer_container(soup)
    results = extract_information(soup)

    if results:
        for i in range(len(house_data['House link'])):
            # Check if the house link already exists in the database
            cursor.execute('''SELECT COUNT(*) FROM houses WHERE house_link = ?''', (house_data['House link'][i],))
            result = cursor.fetchone()
            if result[0] == 0:
                # If the house link doesn't exist, insert it into the database
                cursor.execute('''INSERT INTO houses (house_link, price_per_square_meter) VALUES (?, ?)''',
                            (house_data['House link'][i], house_data['Price per square meter [€]'][i]))
                conn.commit()
            else:
                print(f"House link {house_data['House link'][i]} already exists in the database, and will not be added.")

    house_data['House link'].clear()
    house_data['Price per square meter [€]'].clear()

    #try:
    #    next_page = driver.find_element(By.XPATH, '//a[@aria-label="Next page" and @aria-disabled="false"]')
    #    next_page.click()
    #except:
    #    print('No more pages to click.')
    #    break

    # Add a delay to avoid being blocked by the website
    time.sleep(3)

# Close the connection and quit the driver
conn.close()
driver.quit()
