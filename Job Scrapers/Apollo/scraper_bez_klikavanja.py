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
# options.add_argument("--headless")  # Add this line for headless mode
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

log_in_button = driver.find_element(By.XPATH,'//*[@id="provider-mounter"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/form/div[7]/button')
log_in_button.click()

time.sleep(5)

# XPath for the next page button
next_page_button_xpath = '//*[@id="main-app"]/div[2]/div/div/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div[4]/div/div/div/div/div[3]/div/div[2]/button[2]'

# Number of pages you want to scrape
num_pages_to_scrape = 5  # You can adjust this number based on your requirement

# Variable to keep track of the page number
page_num = 0

# List to store scraped emails
all_data = {
    'Name': [],
    'Job role': [],
    'Company Name': [],
    'Number of Employees': [],
    'Email': [],
}

print("Starting to scrape! :)")

while page_num < num_pages_to_scrape:
    # Increment the page number
    page_num += 1

    web_page = driver.page_source
    soup = BeautifulSoup(web_page, 'html.parser')

    # --------------------- FIRST AND LAST NAME --------------------- #
    names = soup.find_all('div', class_='zp_xVJ20')
    names_clean = [name.find('a').text.strip() for name in names]

    # --------------------- TITLE --------------------- #
    titles = soup.find_all('span', class_='zp_Y6y8d')
    titles_list = [titles[i].text.strip() for i in range(0, len(titles), 2) if titles[i] is not None]

    # --------------------- COMPANY NAME --------------------- #
    company_names = soup.find_all('div', class_='zp_J1j17')
    company_names_clean = [name.find('a').text.strip() for name in company_names]

    # --------------------- PHONE NUMBERS --------------------- #
    phone_numbers = soup.find_all('span', class_='zp_lm1kV')
    phone_numbers_clean = [phone.find('a') for phone in phone_numbers]
    numbers = [phone.text.strip() for phone in phone_numbers_clean if phone is not None]

    # --------------------- NUMBER OF EMPLOYEES --------------------- #
    number_of_employees = soup.find_all('span', class_='zp_Y6y8d')
    numbers_list = [employee.text.strip() for employee in number_of_employees[1::2] if employee is not None]

    # --------------------- EMAILS --------------------- #
    emails = soup.find_all('div', class_='zp_jcL6a')
    emails_list = [email.find('a', class_='zp-link zp_OotKe zp_Iu6Pf').text.strip() if email.find('a', class_='zp-link zp_OotKe zp_Iu6Pf') is not None else '' for email in emails]

    all_data['Name'].extend(names_clean)
    all_data['Job role'].extend(titles_list)
    all_data['Company Name'].extend(company_names_clean)
    all_data['Number of Employees'].extend(numbers_list)
    all_data['Email'].extend(emails_list)

    # If not the last page, click the next page button
    if page_num < num_pages_to_scrape:
        try:
            next_page = driver.find_element(By.XPATH, next_page_button_xpath)
            next_page.click()
            time.sleep(3)  # Add a sleep to give the page time to load
            print(f'Everything is still going as planned. Currently printing {page_num}/{num_pages_to_scrape}.')
        except:
            print("No button to click.")

# Create a DataFrame from the list of emails
df = pd.DataFrame(all_data)

# Save the DataFrame to an Excel file
excel_file_path = 'complete_data.xlsx'

if os.path.isfile(excel_file_path):
    # If the file already exists, load the existing data
    existing_df = pd.read_excel(excel_file_path)

    # Append the new data to the existing DataFrame
    existing_df = existing_df._append(df, ignore_index=True)

    # Save the combined DataFrame back to the same file
    existing_df.to_excel(excel_file_path, index=False)
else:
    # If the file doesn't exist, save the DataFrame as a new file
    df.to_excel(excel_file_path, index=False)

# Close the webdriver
driver.quit()

print(f"Scraped emails saved to {excel_file_path}")

# Removing the duplicates
def remove_duplicates(input_file, output_file):
    # Read Excel file into a DataFrame
    df = pd.read_excel(input_file)

    # Check if there are duplicate rows
    if df.duplicated().any():
        # Identify and remove duplicate rows
        df_no_duplicates = df.drop_duplicates()

        # Save the modified DataFrame to a new Excel file
        df_no_duplicates.to_excel(output_file, index=False)

        print("Duplicate rows removed and saved to", output_file)
    else:
        print("No duplicate rows found. Data remains unchanged.")

if __name__ == "__main__":
    # Specify the input and output file paths
    input_file_path = "complete_data.xlsx"  # Replace with your input file path
    output_file_path = "output_file.xlsx"  # Replace with your desired output file path

    # Call the function to remove duplicates
    remove_duplicates(input_file_path, output_file_path)
