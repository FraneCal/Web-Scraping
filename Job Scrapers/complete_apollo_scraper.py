from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import random
import time
import pandas as pd

# URL of the webpage
URL = "https://app.apollo.io/#/people?finderViewId=5b8050d050a3893c382e9360&contactLabelIds[]=65b56a60f697290001cd6572&prospectedByCurrentTeam[]=yes"

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
email_input.send_keys('YOUR EMAIL')

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

time.sleep(2)

# XPath for the next page button
next_page_button_xpath = '//*[@id="main-app"]/div[2]/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div[4]/div/div/div/div/div[3]/div/div[2]/button[2]'

# Number of pages you want to scrape
num_pages_to_scrape = 1  # You can adjust this number based on your requirement

# Variable to keep track of the page number
page_num = 0

# List to store scraped emails
all_names = []
all_emails = []

while page_num < num_pages_to_scrape:
    # Increment the page number
    page_num += 1

    # Assuming you want the first table, you can use index 0
    tables = driver.find_elements(By.TAG_NAME, 'table')
    if tables:
        table = tables[0]

        # Find all tbody elements inside the table
        tbody_elements = table.find_elements(By.CLASS_NAME, 'zp_RFed0')

        # Loop through each tbody
        for tbody in tbody_elements:
            # Find the fourth td tag with class 'zp_aBhrx' inside the tbody
            td_elements = tbody.find_elements(By.CLASS_NAME, 'zp_aBhrx')
            if len(td_elements) >= 1:
                web_page = driver.page_source
                soup = BeautifulSoup(web_page, 'html.parser')

                names = soup.find_all('div', class_='zp_xVJ20')
                names_clean = [name.find('a').text.strip() for name in names]
                all_names.extend(names_clean)
                print(names_clean)


            # Check if there is a fourth td element
            if len(td_elements) >= 4:
                # Find the first button with type "button" inside the fourth td element
                button = td_elements[3].find_element(By.CSS_SELECTOR, 'button[type="button"]')

                # Click the button
                button.click()

                # Wait for the email to load (you might need to adjust the time based on the page loading speed)
                time.sleep(1)

                web_page = driver.page_source
                soup = BeautifulSoup(web_page, 'html.parser')

                # Scrape the email
                try:
                    emails = soup.find('div', class_='zp_JywRU').find('span', class_='zp_t08Bv').text.strip()
                    all_emails.append(emails)
                except AttributeError:
                    all_emails.append("Email not verified")
                #emails_clean = [email.find('span', class_='zp_t08Bv').text.strip() for email in emails]
                
                #print(emails)

                # Go back to the previous page
                button.click()

        # If not the last page, click the next page button
        if page_num < num_pages_to_scrape:
            try:
                next_page = driver.find_element(By.XPATH, next_page_button_xpath)
                next_page.click()
                time.sleep(2)  # Add a sleep to give the page time to load
            except NoSuchElementException:
                print("No more pages available")
                break

# Create a DataFrame from the list of emails
df = pd.DataFrame({'Emails': all_emails})

# Save the DataFrame to an Excel file
excel_file_path = 'scraped_emails.xlsx'
df.to_excel(excel_file_path, index=False)

# Close the webdriver
driver.quit()

print(f"Scraped emails saved to {excel_file_path}")
