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


def setup_webdriver():
    service = Service()
    options = Options()
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    # options.add_argument("--headless")  # Add this line for headless mode
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def login(driver, email, password):
    driver.get(URL)
    time.sleep(10)  # Wait for the page to load

    email_input = driver.find_element(By.NAME, 'email')
    email_input.click()
    email_input.send_keys(email)

    password_input = driver.find_element(By.NAME, 'password')
    password_input.click()
    password_input.send_keys(password)

    time.sleep(1)

    log_in_button = driver.find_element(By.XPATH,
                                        '//*[@id="provider-mounter"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/form/div[4]/button')
    log_in_button.click()

    time.sleep(5)


def scrape_data(driver, num_pages_to_scrape):
    page_num = 0
    all_data = {
        'Name': [],
        'Job role': [],
        'Company Name': [],
        'Number of Employees': [],
        'Email': [],
    }

    print("Starting to scrape! :)")

    while page_num < num_pages_to_scrape:
        page_num += 1

        web_page = driver.page_source
        soup = BeautifulSoup(web_page, 'html.parser')

        # --------------------- FIRST AND LAST NAME --------------------- #
        names = soup.find_all('div', class_='zp_xVJ20')
        names_clean = [name.find('a').text.strip() for name in names]

        # --------------------- TITLE --------------------- #
        titles = soup.find_all('span', class_='zp_Y6y8d')
        titles_list = [title.text.strip() for title in titles[::3] if title is not None]

        # --------------------- COMPANY NAME --------------------- #
        company_names = soup.find_all('div', class_='zp_J1j17')
        company_names_clean = [name.find('a').text.strip() if name.find('a') is not None else "Company not found" for
                               name in company_names]

        # --------------------- PHONE NUMBERS --------------------- #
        phone_numbers = soup.find_all('span', class_='zp_lm1kV')
        phone_numbers_clean = [phone.find('a') for phone in phone_numbers]
        numbers = [phone.text.strip() for phone in phone_numbers_clean if phone is not None]

        # --------------------- NUMBER OF EMPLOYEES --------------------- #
        number_of_employees = soup.find_all('span', class_='zp_Y6y8d')
        #numbers_list = [employee.text.strip() for employee in number_of_employees[1::2] if employee is not None]
        numbers_list = [employee.text.strip() for employee in number_of_employees if employee.text.strip().replace(',', '').isdigit()]


        # --------------------- EMAILS --------------------- #
        emails = soup.find_all('div', class_='zp_jcL6a')
        emails_list = [email.find('a', class_='zp-link zp_OotKe zp_Iu6Pf').text.strip() if email.find('a',
                                                                                                      class_='zp-link zp_OotKe zp_Iu6Pf') is not None else ''
                       for email in emails]

        all_data['Name'].extend(names_clean)
        all_data['Job role'].extend(titles_list)
        all_data['Company Name'].extend(company_names_clean)
        all_data['Number of Employees'].extend(numbers_list)
        all_data['Email'].extend(emails_list)

        print(len(names_clean))
        print(len(titles_list))
        print(len(company_names_clean))
        print(len(numbers_list))
        print(len(emails_list))

        # If not the last page, click the next page button
        if page_num < num_pages_to_scrape:
            try:
                next_page = driver.find_element(By.XPATH,
                                                '//*[@id="main-app"]/div[2]/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/div[4]/div/div/div/div/div[3]/div/div[2]/button[2]')
                next_page.click()
                time.sleep(3)  # Add a sleep to give the page time to load
                print(f'Everything is still going as planned. Currently printing {page_num}/{num_pages_to_scrape}.')
            except NoSuchElementException:
                print("No button to click.")

    df = pd.DataFrame(all_data)
    return df


def save_to_excel(df, excel_file_path):
    if os.path.isfile(excel_file_path):
        existing_df = pd.read_excel(excel_file_path)

        # Check for duplicates in the existing DataFrame and the new data
        df_no_duplicates = pd.concat([existing_df, df]).drop_duplicates(keep='last')

        df_no_duplicates.to_excel(excel_file_path, index=False)
        print("Data saved to", excel_file_path)
    else:
        df.to_excel(excel_file_path, index=False)
        print("Data saved to", excel_file_path)


def remove_duplicates(input_file, output_file):
    df = pd.read_excel(input_file)
    if df.duplicated().any():
        df_no_duplicates = df.drop_duplicates()
        df_no_duplicates.to_excel(output_file, index=False)
        print("Duplicate rows removed and saved to", output_file)
    else:
        print("No duplicate rows found. Data remains unchanged.")


if __name__ == "__main__":
    URL = "YOUR APOLLO SAVED LIST LINK"

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"]

    driver = setup_webdriver()

    email = 'YOUR APOLLO EMAIL'
    password = 'YOUR APOLLO PASSWORD'
    login(driver, email, password)

    num_pages_to_scrape = 3
    scraped_data = scrape_data(driver, num_pages_to_scrape)

    excel_file_path = 'complete_data.xlsx'
    save_to_excel(scraped_data, excel_file_path)

    driver.quit()

    output_file_path = "output_file.xlsx"
    remove_duplicates(excel_file_path, output_file_path)
