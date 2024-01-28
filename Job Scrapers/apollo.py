# EVERYTHING IS WORKING EXPECT EMAIL

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import random
import time
import pandas as pd

# URL of the webpage
URL = "https://app.apollo.io/#/people?finderViewId=5b6dfc5a73f47568b2e5f11c&contactLabelIds[]=65b56a60f697290001cd6572&prospectedByCurrentTeam[]=yes"

# User agents for browser emulation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    # Add other user agents as needed
]

# Setting up the WebDriver
service = Service()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(service=service, options=options)

# Opening the webpage
driver.get(URL)
time.sleep(10)  # Wait for the page to load

# Logging in
email_input = driver.find_element(By.NAME, 'email')
email_input.click()
email_input.send_keys('YOUR EMAIL ADRESS')

password_input = driver.find_element(By.NAME, 'password')
password_input.click()
password_input.send_keys('YOUR PASSWORD')

time.sleep(1)

log_in_button = driver.find_element(By.XPATH, '//*[@id="provider-mounter"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/form/div[7]/button')
log_in_button.click()

time.sleep(5)

# Hiding filters
hide_filters = driver.find_element(By.XPATH, '//*[@id="main-app"]/div[2]/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div[2]/div/div[2]/div/span/button/div/div/span')
hide_filters.click()

# XPath for the next page button
next_page_button_xpath = '//*[@id="main-app"]/div[2]/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div[4]/div/div/div/div/div[3]/div/div[2]/button[2]'

# Number of pages you want to scrape
num_pages_to_scrape = 4  # You can adjust this number based on your requirement

all_data = {
    'Name': [],
    'Company Name': [],
    'Phone Number': [],
    'Number of Employees': [],
}

for page_num in range(num_pages_to_scrape):
    # Scrape data from the current page
    web_page = driver.page_source
    soup = BeautifulSoup(web_page, 'html.parser')

    # Extracting data from the HTML

    # --------------------- FIRST AND LAST NAME --------------------- #
    f_l_name = soup.find_all('div', class_='zp_xVJ20')
    f_l_name_clean = [f_l.find('a').text.strip() for f_l in f_l_name]

    # --------------------- COMPANY NAME --------------------- #
    company_names = soup.find_all('div', class_='zp_J1j17')
    company_names_clean = [name.find('a').text.strip() for name in company_names]

    # --------------------- PHONE NUMBERS --------------------- #
    phone_numbers = soup.find_all('span', class_='zp_lm1kV')
    phone_numbers_clean = [phone.find('a') for phone in phone_numbers]
    numbers = [phone.text.strip() for phone in phone_numbers_clean if phone is not None]

    # # --------------------- EMAILS --------------------- #
    # emails = soup.find_all('div', class_='zp_JywRU')
    # emails_clean = [email.find('span', class_='zp_t08Bv').text.strip() for email in emails]

    # --------------------- NUMBER OF EMPLOYEES --------------------- #
    number_of_employees = soup.find_all('span', class_='zp_Y6y8d')
    employees = [employee.text.strip() for employee in number_of_employees]
    numbers_only = employees[2::3]

    all_data['Name'].extend(f_l_name_clean)
    all_data['Company Name'].extend(company_names_clean)
    all_data['Phone Number'].extend(numbers)
    # all_data['Email'].extend(emails_clean)
    all_data['Number of Employees'].extend(numbers_only)

    # If not the last page, click the next page button
    if page_num < num_pages_to_scrape - 1:
        try:
            next_page = driver.find_element(By.XPATH, next_page_button_xpath)
            next_page.click()
            time.sleep(3)  # Add a sleep to give the page time to load
        except NoSuchElementException:
            print("No more pages available")
            break

# Close the webdriver
driver.quit()

# Create a DataFrame from the collected data
df = pd.DataFrame(all_data)

# Save the DataFrame to an Excel file
df.to_excel('apollo_data.xlsx', index=False)
