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
driver = webdriver.Chrome(service=service, options=options)

# Opening the webpage
driver.get(URL)
time.sleep(10)  # Wait for the page to load

# Logging in
email_input = driver.find_element(By.NAME, 'email')
email_input.click()
email_input.send_keys('YOUR EMAIL')

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
num_pages_to_scrape = 2  # You can adjust this number based on your requirement

# Variable to keep track of the page number
page_num = 0

# List to store scraped emails
all_data = {
    'Company name': [],
    'Domain': [],
}

print("Starting to scrape! :)")

while page_num < num_pages_to_scrape:
    # Increment the page number
    page_num += 1
    
    web_page = driver.page_source
    soup = BeautifulSoup(web_page, 'html.parser')

    # --------------------- COMPANY NAME --------------------- #
    company_names = soup.find_all('div', class_='zp_J1j17')
    company_names_clean = [name.find('a').text.strip() for name in company_names]

    # --------------------- DOMAIN --------------------- #
    domains = soup.find_all('div', class_='zp_I1ps2')
    domains_clean = [domain.find('a', class_='zp-link zp_OotKe').get('href') for domain in domains]

    all_data['Company name'].extend(company_names_clean)
    all_data['Domain'].extend(domains_clean)
  
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
            time.sleep(3)  # Add a sleep to give the page time to load
            print(f'Everything is still going as planned.')
        except:
            print("No button to click.")


# Close the webdriver
driver.quit()

print(f"Scraped emails saved to {excel_file_path}")
