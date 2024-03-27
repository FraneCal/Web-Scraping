# https://github.com/peduajo/geetest-slice-captcha-solver

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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import session
import base64
import re
import sys
from solver import PuzleSolver
from dotenv import load_dotenv
import os

load_dotenv()

def solve_captcha_slider(driver):
    # Execute JavaScript to get the Base64-encoded image data
    background_image_data = driver.execute_script(
        "return arguments[0].toDataURL('image/png').substring(21);",
        driver.find_element(By.CSS_SELECTOR, ".geetest_canvas_bg.geetest_absolute")
    )
    slice_image_data = driver.execute_script(
        "return arguments[0].toDataURL('image/png').substring(21);",
        driver.find_element(By.CSS_SELECTOR, ".geetest_canvas_slice.geetest_absolute")
    )

    # Decode the Base64-encoded image data into bytes
    background_image_bytes = base64.b64decode(background_image_data)
    slice_image_bytes = base64.b64decode(slice_image_data)

    # Save the images to files
    with open('background.png', 'wb') as background_file:
        background_file.write(background_image_bytes)

    with open('piece.png', 'wb') as piece_file:
        piece_file.write(slice_image_bytes)

    solver = PuzleSolver("piece.png", "background.png")
    solution = solver.get_position()
    print(solution)

    try:
        slider = driver.find_element(By.CLASS_NAME, 'geetest_slider_button')
        for x in range(0, 260, 43):
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
    wait = WebDriverWait(driver, 5)
    while True:
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "article button.button"))).click()

        except TimeoutException:
            break

    time.sleep(2)
    containers = soup.find_all('div',
                               class_='grid-item palm-one-whole lap-one-half desk-one-half grouped-listing-frame')
    for container in containers:
        informations = container.find_all('span')

        links = container.find_all('a', class_='block')
        links_list = [f"https://www.immobilienscout24.de{link.get('href')}" for link in links]
        links_set = set(links_list)

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
                        square_meter_str = square_meter_text.replace('m²', '').strip()

                        # Remove all commas
                        square_meter_str = square_meter_str.replace(',', '.')

                        # Replace the first dot with an empty string to prevent decimal issues
                        if square_meter_str.count('.') == 2:
                            square_meter_str = square_meter_str.replace('.', '', 1)

                        # Check if there are three digits after the dot and remove the dot if true
                        if '.' in square_meter_str and len(square_meter_str.split('.')[1]) == 3:
                            square_meter_str = square_meter_str.replace('.', '', 1)

                        # Convert square meter to float
                        square_meter = float(square_meter_str) if square_meter_str else 0.0

                        # Check if square_meter is non-zero before division
                        if square_meter != 0:
                            price_per_square_meter = round(price / square_meter, 2)

                            # Check if price_per_square_meter is within the specified range
                            if 2000 <= price_per_square_meter <= 3000:
                                # Append data to the list for saving to Excel
                                house_data['House link'].extend(links_set)
                                house_data['Price per square meter [€]'].append(price_per_square_meter)

                    except (ValueError, IndexError):
                        # print("Price or the living space information is missing or invalid.")
                        pass

    return house_data


def extract_information_apartments(soup):
    try:
        # Find links inside the information div
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
                    # Remove square meter sign and convert to float
                    square_meter_str = text.replace('m²', '').strip()

                    # Remove all commas
                    square_meter_str = square_meter_str.replace(',', '.')

                    # Replace the first dot with an empty string to prevent decimal issues
                    if square_meter_str.count('.') == 2:
                        square_meter_str = square_meter_str.replace('.', '', 1)

                    # Check if there are three digits after the dot and remove the dot if true
                    if '.' in square_meter_str and len(square_meter_str.split('.')[1]) == 3:
                        square_meter_str = square_meter_str.replace('.', '', 1)

                    # Convert square meter to float
                    square_meter = float(square_meter_str) if square_meter_str else 0.0

                    # Check if square_meter is non-zero before division
                    if square_meter != 0:
                        price_per_square_meter = round(price / square_meter, 2)

                        # Check if price_per_square_meter is within the specified range
                        if 2000 <= price_per_square_meter <= 3000:
                            # Append data to the list for saving to Excel
                            house_data['House link'].append(house_link)
                            house_data['Price per square meter [€]'].append(price_per_square_meter)
            except Exception as e:
                print(f"Error occurred: {e}")
                print("Price or the living space information is missing.")

    except Exception as e:
        print(f"Error occurred while extracting links: {e}")

    return house_data


def extract_information_house(soup):
    # Find all containers
    containers = soup.find_all('div', class_='grid grid-flex grid-align-center grid-justify-space-between')

    # Iterate over containers
    for container in containers:
        # Find all dd elements within the container
        informations = container.find_all('dd')

        # Extract links from a elements within the container
        links = container.find_all('a')
        links_list = [f"https://www.immobilienscout24.de{link.get('href')}" for link in links]
        links_set = set(links_list)

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
                        square_meter_str = square_meter_text.replace('m²', '').strip()

                        # Remove all commas
                        square_meter_str = square_meter_str.replace(',', '.')

                        # Replace the first dot with an empty string to prevent decimal issues
                        if square_meter_str.count('.') == 2:
                            square_meter_str = square_meter_str.replace('.', '', 1)

                        # Check if there are three digits after the dot and remove the dot if true
                        if '.' in square_meter_str and len(square_meter_str.split('.')[1]) == 3:
                            square_meter_str = square_meter_str.replace('.', '', 1)

                        # Convert square meter to float
                        square_meter = float(square_meter_str) if square_meter_str else 0.0

                        # Check if square_meter is non-zero before division
                        if square_meter != 0:
                            price_per_square_meter = round(price / square_meter, 2)

                            # Check if price_per_square_meter is within the specified range
                            if 2000 <= price_per_square_meter <= 3000:
                                # Append data to the list for saving to Excel
                                house_data['House link'].extend(links_set)
                                house_data['Price per square meter [€]'].append(price_per_square_meter)

                    except (ValueError, IndexError):
                        # print("Price or the living space information is missing or invalid.")
                        pass

    return house_data


def send_email(new_links):
    my_email = os.getenv("MY_EMAIL")
    password = os.getenv("PASSWORD")

    message = MIMEMultipart()
    message['From'] = my_email
    message['To'] = os.getenv("RECIPIENT_EMAIL")
    message['Subject'] = 'New Apartments Added'

    body = "\n".join(new_links)
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs='fcalus00@fesb.hr',
                            msg=message.as_string())


def check_words_in_link_content(cursor, exclude_words):
    # Fetch all links from the database
    cursor.execute('''SELECT house_link FROM houses''')
    links_to_check = cursor.fetchall()

    for link_row in links_to_check:
        link = link_row[0]
        # Scrape the content of the link using BeautifulSoup
        driver.get(link)
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Extract text content and clean it
        text_content = soup.get_text(strip=True)
        text_content = re.sub(r'\s+', ' ', text_content)  # Remove extra whitespaces
        
        # Check if the link contains any of the exclude words
        if any(word.lower() in text_content.lower() for word in exclude_words):
            # If any exclude word is found, remove the link from the database
            try:
                cursor.execute('''DELETE FROM houses WHERE house_link = ?''', (link,))
                conn.commit()  # Commit the transaction
                print(f"Link removed from database: {link}")
            except sqlite3.Error as e:
                print(f"Error occurred while deleting link: {e}")


# Create SQLite connection and cursor
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS houses (
                    id INTEGER PRIMARY KEY,
                    house_link TEXT,
                    price_per_square_meter REAL
                )''')

base_url = sys.argv[4]

start_page = 1

# Generate fake user agents
options = Options()
ua = UserAgent()
user_agent = ua.random

options.add_argument(f'--user-agent={user_agent}')
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
actions = ActionChains(driver)
driver.get(base_url)

# Click captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

time.sleep(4)

# Solve captcha slider
#solve_captcha_slider(driver)

time.sleep(4)

# Accept cookies
accept_cookies(driver)

new_links = []

counter = 0

while True:
    counter += 1
    print(f'Extracting infromation from page: {counter}')
    # Extract information from the current page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    special_offer_results = special_offer_container(soup)

    if "wohnung" in base_url:
        results = extract_information_apartments(soup)
    elif "haus" in base_url:
        results = extract_information_house(soup)
    else:
        print('No Wohnung or Haus in the URL.')

    if results:
        if len(house_data['House link']) == len(house_data['Price per square meter [€]']):
            for i in range(len(house_data['House link'])):
                # Check if the house link already exists in the database
                cursor.execute('''SELECT COUNT(*) FROM houses WHERE house_link = ?''', (house_data['House link'][i],))
                result = cursor.fetchone()
                if result[0] == 0:
                    # If the house link doesn't exist, insert it into the database
                    cursor.execute('''INSERT INTO houses (house_link, price_per_square_meter) VALUES (?, ?)''',
                                   (house_data['House link'][i], house_data['Price per square meter [€]'][i]))
                    conn.commit()
                    new_links.append(house_data['House link'][i])

            new_links.extend(house_data['House link'])

    # Move to the next page
    try:
        next_page = driver.find_element(By.XPATH, '//a[@aria-label="Next page" and @aria-disabled="false"]')
        next_page.click()
    except:
        print('No more pages to click.')
        break

    house_data['House link'].clear()
    house_data['Price per square meter [€]'].clear()

    time.sleep(3)


# Check if any links need to be removed based on their content
exclude_words = [sys.argv[5]]
check_words_in_link_content(cursor, exclude_words)

# Close the connection and quit the driver
conn.close()
driver.quit()

# Send email with all new links
if new_links:
    send_email(new_links)
