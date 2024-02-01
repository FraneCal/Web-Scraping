from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import random
import time
import pandas as pd
import os

# URL of the webpage
URL = "YOUR APOLLO SAVED LIST LINK"

# User agents for browser emulation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
]

# Setting up the WebDriver
service = Service()
options = Options()
options.add_argument(f"user-agent={random.choice(user_agents)}")
#options.add_argument("--headless")  # Add this line for headless mode
driver = webdriver.Chrome(service=service, options=options)

# Opening the webpage
driver.get(URL)
time.sleep(10)  # Wait for the page to load

# Logging in
email_input = driver.find_element(By.NAME, 'email')
email_input.click()
email_input.send_keys('YOUR USERNAME')

password_input = driver.find_element(By.NAME, 'password')
password_input.click()
password_input.send_keys('YOUR PASSWORD')

time.sleep(1)

log_in_button = driver.find_element(By.XPATH, '//*[@id="provider-mounter"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/form/div[7]/button')
log_in_button.click()

time.sleep(5)

# XPath for the next page button
next_page_button_xpath = '//*[@id="main-app"]/div[2]/div/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div[4]/div/div/div/div/div[3]/div/div[2]/button[2]'

# Number of pages you want to scrape
num_pages_to_scrape = 3  # You can adjust this number based on your requirement

# Variable to keep track of the page number
page_num = 0

# List to store scraped emails
all_data = {
    'Name': [],
    'Job role': [],
    'Company Name': [],
    'Phone Number': [],
    'Number of Employees': [],
    'Email': [],
}

print("Starting to scrape! :)")
while page_num < num_pages_to_scrape:
    # Increment the page number
    page_num += 1

    # Assuming you want the first table, you can use index 0
    tables = driver.find_elements(By.TAG_NAME, 'table')
    if tables:
        table = tables[0]

        # Find all tbody elements inside the table
        tbody_elements = table.find_elements(By.CLASS_NAME, 'zp_RFed0')

        web_page = driver.page_source
        soup = BeautifulSoup(web_page, 'html.parser')

        # --------------------- FIRST AND LAST NAME --------------------- #
        names = soup.find_all('div', class_='zp_xVJ20')
        names_clean = [name.find('a').text.strip() for name in names]

        # --------------------- TITLE --------------------- #
        titles = soup.find_all('span', class_='zp_Y6y8d')
        titles_list = [title.text.strip() for title in titles if title is not None]
        titles_clean = titles_list[::3]

        # --------------------- COMPANY NAME --------------------- #
        company_names = soup.find_all('div', class_='zp_J1j17')
        company_names_clean = [name.find('a').text.strip() for name in company_names]

        # --------------------- PHONE NUMBERS --------------------- #
        phone_numbers = soup.find_all('span', class_='zp_lm1kV')
        phone_numbers_clean = [phone.find('a') for phone in phone_numbers]
        numbers = [phone.text.strip() for phone in phone_numbers_clean if phone is not None]

        # --------------------- NUMBER OF EMPLOYEES --------------------- #
        number_of_employees = soup.find_all('span', class_='zp_Y6y8d')
        employees = [employee.text.strip() for employee in number_of_employees]
        numbers_only = employees[2::3]

        all_data['Name'].extend(names_clean)
        all_data['Job role'].extend(titles_clean)
        all_data['Company Name'].extend(company_names_clean)
        all_data['Phone Number'].extend(numbers)
        all_data['Number of Employees'].extend(numbers_only)

        # Loop through each tbody
        for tbody in tbody_elements:
            # Find the fourth td tag with class 'zp_aBhrx' inside the tbody
            td_elements = tbody.find_elements(By.CLASS_NAME, 'zp_aBhrx')

            # Check if there is a fourth td element
            if len(td_elements) >= 4:
                # Find the first button with type "button" inside the fourth td element
                button = td_elements[3].find_element(By.CSS_SELECTOR, 'button[type="button"]')

                # Click the button
                button.click()

                time.sleep(1)

                web_page = driver.page_source
                soup = BeautifulSoup(web_page, 'html.parser')

                # Scrape the email
                try:
                    emails = soup.find('div', class_='zp_JywRU').find('span', class_='zp_t08Bv').text.strip()
                    all_data['Email'].append(emails)
                except AttributeError:
                    all_data['Email'].append("Email not verified")

                # Go back to the previous page
                button.click()
        
        # Create a DataFrame from the list of emails
        df = pd.DataFrame(all_data)

        # Save the DataFrame to an Excel file
        excel_file_path = 'complete_data.xlsx'

        # If the file already exists, load the existing data
        if os.path.isfile(excel_file_path):
            existing_df = pd.read_excel(excel_file_path)

        # Append the new data to the existing DataFrame
            existing_df = existing_df._append(df, ignore_index=True)

        # Save the combined DataFrame back to the same file
            existing_df.to_excel(excel_file_path, index=False)
        else:
        # If the file doesn't exist, save the DataFrame as a new file
            df.to_excel(excel_file_path, index=False)

        print(f'Data from page {page_num} successfully saved.')

        # If not the last page, click the next page button
        if page_num < num_pages_to_scrape:
            try:
                next_page = driver.find_element(By.XPATH, next_page_button_xpath)
                next_page.click()
                time.sleep(2)  # Add a sleep to give the page time to load
                print(f'Everything is still as planned. :)')
            except NoSuchElementException:
                print("No more pages available")
                break

# Close the webdriver
driver.quit()

print(f"Scraped completed.")
