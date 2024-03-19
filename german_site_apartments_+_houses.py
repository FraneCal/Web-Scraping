# -------------------------------------------- FIX SPECIAL PRICES FUNCTION -------------------------------------------- #


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
        # POPRAVI DA PROSIRI SVE
        show_more_units = driver.find_element(By.XPATH, '//*[@id="result-p-149369723"]/div[3]/button')
        show_more_units.click()
        print("Show more button clicked.")

        time.sleep(2)
        containers = soup.find_all('div', class_='grid grid-flex grid-justify-space-between')
        for container in containers:
            informations = container.find_all('span')

            # DOBIVAS DUPLIKATE, RIJESI
            links = container.find_all('a', class_='block')
            links_list = [f"https://www.immobilienscout24.de{link.get('href')}" for link in links]
            #print(links_list)

            variable = [information.getText() for information in informations]

            # Extract price and square meter information from the correct positions
            for i in range(0, len(variable), 2):
                # Check if there are enough elements in the variable list
                if i + 1 < len(variable):
                    price_text = variable[i]
                    square_meter_text = variable[i + 1]
                    #print(f"0. {square_meter_text}")

                    # Check if both price and square meter information are present
                    if price_text and square_meter_text:
                        try:
                            # Remove euro sign and convert price to int
                            price = int(price_text.replace('€', '').replace('.', '').replace(',', '').strip())

                            # Remove square meter sign and convert to float
                            square_meter_str = square_meter_text.replace('m²', '').replace(',', '').strip()
                            #print(f"1. {square_meter_str}")

                             # Handle cases where dot is used as a thousand separator
                            if '.' in square_meter_str and square_meter_str.count('.') == 1:
                                # If there is only one dot, consider it as a thousand separator
                                square_meter_str = square_meter_str.replace('.', '')
                            elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                                # If there are multiple dots, keep only the last one as the decimal point
                                square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace(
                                    '.', '')
                                #print(f"3. {square_meter_str}")

                            # Convert square meter to float
                            square_meter = float(square_meter_str) if square_meter_str else 0.0
                            #print(f"4. {square_meter}")

                            # Check if square_meter is non-zero before division
                            if square_meter != 0:
                                price_per_square_meter = round(price / square_meter, 2)

                                # Check if price_per_square_meter is within the specified range
                                if 2000 <= price_per_square_meter <= 3000:
                                    # Append data to the list for saving to Excel
                                    house_data['House link'].extend(links_list)
                                    house_data['Price per square meter [€]'].append(price_per_square_meter)
                        except (ValueError, IndexError):
                            #print("Price or the living space information is missing or invalid.")
                            pass
    except:
        pass
    
    return house_data


def extract_information_apartments(soup):
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
                # Remove square meter sign and convert to int
                square_meter_str = text.replace('m²', '').replace(',', '').strip()

                # Handle cases where dot is used as a thousand separator
                if '.' in square_meter_str and square_meter_str.count('.') == 1:
                    # If there is only one dot, consider it as a thousand separator
                    square_meter_str = square_meter_str.replace('.', '')
                elif '.' in square_meter_str and square_meter_str.count('.') > 1:
                    # If there are multiple dots, keep only the last one as the decimal point
                    square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace(
                        '.', '')

                # Convert to float, handle the case when it's zero
                square_meter = float(square_meter_str) if square_meter_str else 0.0

                # Check if square_meter is non-zero before division
                if square_meter != 0:
                    price_per_square_meter = round(price / square_meter, 2)

                    # Check if price_per_square_meter is within the specified range
                    if 2000 <= price_per_square_meter <= 3000:
                        # Append data to the list for saving to Excel
                        house_data['House link'].append(house_link)
                        house_data['Price per square meter [€]'].append(price_per_square_meter)
        except:
            print("Price or the living space information is missing.")

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

        # Extract text from dd elements
        variable = [information.getText() for information in informations]

        # Extract price and square meter information from the correct positions
        for i in range(0, len(variable), 2):
            # Check if there are enough elements in the variable list
            if i + 1 < len(variable):
                price_text = variable[i]
                square_meter_text = variable[i + 1]
                print(f"0. {square_meter_text}")
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
                        square_meter = float(square_meter_str)
                        print(f"4. {square_meter}")
                        
                        # Check if square_meter is non-zero before division
                        if square_meter != 0:
                            price_per_square_meter = round(price / square_meter, 2)
        
                            print(square_meter)
            
                            # Check if price_per_square_meter is within the specified range
                            if 2000 <= price_per_square_meter <= 3000:
                                # Append data to the list for saving to Excel
                                house_data['House link'].extend(links_list)
                                house_data['Price per square meter [€]'].append(price_per_square_meter)
                    except (ValueError, IndexError):
                        #print("Price or the living space information is missing or invalid.")
                        pass

    return house_data


def send_email(new_links):
    my_email = "franecalusic94@gmail.com"
    password = "jmyxbqpbrzlteway"

    message = MIMEMultipart()
    message['From'] = my_email
    message['To'] = 'fcalus00@fesb.hr'
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
        text_content = soup.get_text()

        # Check if the link contains any of the exclude words
        if any(word.lower() in text_content.lower() for word in exclude_words):
            # If any exclude word is found, remove the link from the database
            cursor.execute('''DELETE FROM houses WHERE house_link = ?''', (link,))
            print(f"Link removed from database: {link}")


# Create SQLite connection and cursor
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS houses (
                    id INTEGER PRIMARY KEY,
                    house_link TEXT,
                    price_per_square_meter REAL
                )''')

# # Ask the user for input
# while True:
#     city = input("Enter the city you want to search for: ").lower()
#     if city != "":
#         break
#     else:
#         print("City name cannot be empty. Please enter a valid city name.")
#
# subregion = input("Enter the subregion (optional, press Enter to skip): ").lower()
#
# while True:
#     apart_or_house = input("Enter what you are buying (wohnung or haus): ").lower()
#     if apart_or_house == "wohnung" or apart_or_house == "haus":
#         break
#     else:
#         print("Please enter either 'wohnung' or 'haus'.")
#
# if subregion:
#     base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/{subregion}/wohnung-kaufen"
# else:
#     base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/wohnung-kaufen"

base_url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/steglitz-zehlendorf/wohnung-kaufen?enteredFrom=one_step_search'
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

# Wait for the page to load
time.sleep(5)

# Click captcha
captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
captcha.click()

time.sleep(4)

# Solve captcha slider
solve_captcha_slider(driver)

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

    print("Stuck before extracting the prices and square meters.")

    special_offer_results = special_offer_container(soup)

    if "wohnung" in base_url:
        results = extract_information_apartments(soup)
    elif "haus" in base_url:
        results = extract_information_house(soup)
    else:
        print('No Wohnung or Haus in the URL.')

    print("Stuck before entering the database.")
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
                new_links.append(house_data['House link'][i])

        new_links.extend(house_data['House link'])

    print("Stuck before next page.")
    # Move to the next page
    try:
        next_page = driver.find_element(By.XPATH, '//a[@aria-label="Next page" and @aria-disabled="false"]')
        next_page.click()
    except:
        print('No more pages to click.')
        break

    # # Move to the next page
    # current_page += 1
    # next_url = f'{base_url}?pagenumber={current_page}'
    # driver.get(next_url)

    # # Extract and print the current page number
    # print(f"Scraping page number: {current_page}")

    house_data['House link'].clear()
    house_data['Price per square meter [€]'].clear()

    # Add a delay to avoid being blocked by the website
    time.sleep(3)

# Check if any links need to be removed based on their content
check_words_in_link_content(cursor, ["Zwangsversteigerungen", "Dachrohling"])

# Close the connection and quit the driver
conn.close()
driver.quit()

# Send email with all new links
if new_links:
    send_email(new_links)








# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver import ActionChains
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.chrome.options import Options
# from fake_useragent import UserAgent
# import time
# import sqlite3
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


# def solve_captcha_slider(driver):
#     try:
#         slider = driver.find_element(By.CLASS_NAME, 'geetest_slider_button')
#         attempt_counter = 0

#         while attempt_counter < 6:
#             actions.move_to_element(slider).click_and_hold().move_by_offset(10, 0).release().perform()
#             time.sleep(0.1)

#             # Check if puzzle captcha is still present
#             if EC.presence_of_element_located((By.CLASS_NAME, 'geetest_radar_tip'))(driver):
#                 attempt_counter += 1
#             else:
#                 break

#     except:
#         print('No slider found. Continuing with the code.')


# def accept_cookies(driver):
#     try:
#         def get_shadow_root(element):
#             return driver.execute_script('return arguments[0].shadowRoot', element)

#         shadow_host = driver.find_element(By.ID, 'usercentrics-root')
#         button = get_shadow_root(shadow_host).find_element(By.CSS_SELECTOR, '[data-testid=uc-accept-all-button]')
#         button.click()
#     except:
#         print("Accept cookies not found.")


# house_data = {
#     'House link': [],
#     'Price per square meter [€]': [],
# }


# def special_offer_container(soup):
#     # Looking for special offer container
#     try:
#         for _ in range(2):
#             # Show all of the offers in the special offer container
#             show_more_units = driver.find_element(By.CLASS_NAME, 'padding-left-none link-text-secondary button')
#             show_more_units.click()

#         time.sleep(1)
#         containers = soup.find_all('div', class_='grid grid-flex grid-justify-space-between')
#         links_container = [container.find('a')['href'] for container in containers]
#         for link_container, info_container in zip(links_container, containers):
#             house_link_container = f"https://www.immobilienscout24.de{link_container}"
#             print(house_link_container)

#             text_container = info_container.getText().strip()
#             print(text_container)
#             try:
#                 if '€' in text_container:
#                     # Remove euro sign and convert to int
#                     price = int(text_container.replace('€', '').replace('.', '').replace(',', '').strip())
#                     print(price)
#                 elif 'm²' in text_container:
#                     # Remove square meter sign and convert to int
#                     square_meter_str = text_container.replace('m²', '').replace(',', '').strip()
#                     print(square_meter_str)

#                     # Handle cases where dot is used as a thousand separator
#                     if '.' in square_meter_str and square_meter_str.count('.') == 1:
#                         # If there is only one dot, consider it as a thousand separator
#                         square_meter_str = square_meter_str.replace('.', '')
#                     elif '.' in square_meter_str and square_meter_str.count('.') > 1:
#                         # If there are multiple dots, keep only the last one as the decimal point
#                         square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[
#                             1].replace('.', '')

#                     # Convert to float, handle the case when it's zero
#                     square_meter = float(square_meter_str) if square_meter_str else 0.0

#                     # Check if square_meter is non-zero before division
#                     if square_meter != 0:
#                         price_per_square_meter = round(price / square_meter, 2)

#                         # Check if price_per_square_meter is within the specified range
#                         if 2000 <= price_per_square_meter <= 3000:
#                             # Append data to the list for saving to Excel
#                             house_data['House link'].append(house_link_container)
#                             house_data['Price per square meter [€]'].append(price_per_square_meter)
#             except:
#                 print("Special offer price or the living space information is missing.")

#     except:
#         print('No special offers found.')

#     return house_data


# def extract_information(soup):
#     # Find links inside the information div
#     information = soup.find_all('dd', class_='font-highlight font-tabular')
#     links = [info.find_previous('div', class_='grid-item').find('a')['href'] for info in information]

#     for link, info in zip(links, information):
#         house_link = f"https://www.immobilienscout24.de{link}"

#         # Extract and print only the prices and square meters
#         text = info.getText().strip()
#         try:
#             if '€' in text:
#                 # Remove euro sign and convert to int
#                 price = int(text.replace('€', '').replace('.', '').replace(',', '').strip())
#             elif 'm²' in text:
#                 # Remove square meter sign and convert to int
#                 square_meter_str = text.replace('m²', '').replace(',', '').strip()

#                 # Handle cases where dot is used as a thousand separator
#                 if '.' in square_meter_str and square_meter_str.count('.') == 1:
#                     # If there is only one dot, consider it as a thousand separator
#                     square_meter_str = square_meter_str.replace('.', '')
#                 elif '.' in square_meter_str and square_meter_str.count('.') > 1:
#                     # If there are multiple dots, keep only the last one as the decimal point
#                     square_meter_str = square_meter_str.rsplit('.', 1)[0] + square_meter_str.rsplit('.', 1)[1].replace(
#                         '.', '')

#                 # Convert to float, handle the case when it's zero
#                 square_meter = float(square_meter_str) if square_meter_str else 0.0

#                 # Check if square_meter is non-zero before division
#                 if square_meter != 0:
#                     price_per_square_meter = round(price / square_meter, 2)

#                     # Check if price_per_square_meter is within the specified range
#                     if 2000 <= price_per_square_meter <= 3000:
#                         # Append data to the list for saving to Excel
#                         house_data['House link'].append(house_link)
#                         house_data['Price per square meter [€]'].append(price_per_square_meter)
#         except:
#             print("Price or the living space information is missing.")

#     return house_data

# def send_email(new_links):
#     my_email = "franecalusic94@gmail.com"
#     password = "jmyxbqpbrzlteway"

#     message = MIMEMultipart()
#     message['From'] = my_email
#     message['To'] = 'fcalus00@fesb.hr'
#     message['Subject'] = 'New Apartments Added'

#     body = "\n".join(new_links)
#     message.attach(MIMEText(body, 'plain'))

#     with smtplib.SMTP('smtp.gmail.com', 587) as connection:
#         connection.starttls()
#         connection.login(user=my_email, password=password)
#         connection.sendmail(from_addr=my_email,
#                             to_addrs='fcalus00@fesb.hr',
#                             msg=message.as_string())


# # Create SQLite connection and cursor
# conn = sqlite3.connect('database.db')
# cursor = conn.cursor()

# # Create table if it doesn't exist
# cursor.execute('''CREATE TABLE IF NOT EXISTS houses (
#                     id INTEGER PRIMARY KEY,
#                     house_link TEXT,
#                     price_per_square_meter REAL
#                 )''')

# # # Ask the user for input
# # while True:
# #     city = input("Enter the city you want to search for: ").lower()
# #     if city != "":
# #         break
# #     else:
# #         print("City name cannot be empty. Please enter a valid city name.")
# #
# # subregion = input("Enter the subregion (optional, press Enter to skip): ").lower()
# #
# # while True:
# #     apart_or_house = input("Enter what you are buying (wohnung or haus): ").lower()
# #     if apart_or_house == "wohnung" or apart_or_house == "haus":
# #         break
# #     else:
# #         print("Please enter either 'wohnung' or 'haus'.")
# #
# # if subregion:
# #     base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/{subregion}/wohnung-kaufen"
# # else:
# #     base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/wohnung-kaufen"

# base_url = 'https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-kaufen'
# start_page = 1

# # Generate fake user agents
# options = Options()
# ua = UserAgent()
# user_agent = ua.random

# options.add_argument(f'--user-agent={user_agent}')
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-gpu")

# driver = webdriver.Chrome(options=options)
# actions = ActionChains(driver)
# driver.get(base_url)

# # Wait for the page to load
# time.sleep(5)

# # Click captcha
# captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
# captcha.click()

# time.sleep(4)

# # Solve captcha slider
# solve_captcha_slider(driver)

# time.sleep(4)

# # Accept cookies
# accept_cookies(driver)

# new_links = []

# while True:
#     # Extract information from the current page
#     page_source = driver.page_source
#     soup = BeautifulSoup(page_source, "html.parser")
#     special_offer_results = special_offer_container(soup)
#     results = extract_information(soup)

#     if results:
#         for i in range(len(house_data['House link'])):
#             # Check if the house link already exists in the database
#             cursor.execute('''SELECT COUNT(*) FROM houses WHERE house_link = ?''', (house_data['House link'][i],))
#             result = cursor.fetchone()
#             if result[0] == 0:
#                 # If the house link doesn't exist, insert it into the database
#                 cursor.execute('''INSERT INTO houses (house_link, price_per_square_meter) VALUES (?, ?)''',
#                                (house_data['House link'][i], house_data['Price per square meter [€]'][i]))
#                 conn.commit()
#                 new_links.append(house_data['House link'][i])

#         new_links.extend(new_links)

#     house_data['House link'].clear()
#     house_data['Price per square meter [€]'].clear()

#     # Move to the next page
#     try:
#         next_page = driver.find_element(By.XPATH, '//a[@aria-label="Next page" and @aria-disabled="false"]')
#         next_page.click()
#     except:
#         print('No more pages to click.')
#         break

#     # # Move to the next page
#     # current_page += 1
#     # next_url = f'{base_url}?pagenumber={current_page}'
#     # driver.get(next_url)

#     # # Extract and print the current page number
#     # print(f"Scraping page number: {current_page}")

#     # Add a delay to avoid being blocked by the website
#     time.sleep(3)


# # Close the connection and quit the driver
# conn.close()
# driver.quit()

# # Send email with all new links
# if new_links:
#     send_email(new_links)
