import requests
import csv

url = 'https://api.thecompaniesapi.com/v1/companies/similar'
headers = {'Authorization': 'Basic 3C69nnR1'}

input_csv_file = 'domain_names.csv'
output_csv_file = 'output_data.csv'

try:
    with open(input_csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header if present
        output_data = [['Domain', 'Main Industry']]

        for row in reader:
            domain = row[0]
            param = {'domains[]': domain}

            try:
                response = requests.get(url, headers=headers, params=param)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                data = response.json()

                if 'companies' in data and data['companies']:
                    main_industry = data['companies'][0]['industryMain']
                    output_data.append([domain, main_industry])
                else:
                    output_data.append([domain, 'Industry not found'])
                    print(f"No company data found for domain {domain}")

            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error for domain {domain}:", errh)
            except requests.exceptions.RequestException as err:
                print(f"Request Error for domain {domain}:", err)

    # Save results to a new CSV file
    with open(output_csv_file, 'w', newline='') as output_csv:
        writer = csv.writer(output_csv)
        writer.writerows(output_data)

except FileNotFoundError:
    print(f"Error: The file '{input_csv_file}' does not exist.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")





# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import time

# URL = "https://www.google.com/"

# driver = webdriver.Chrome()
# driver.get(URL)
# driver.maximize_window()

# time.sleep(3)

# accept_cookies = driver.find_element(By.XPATH, '//*[@id="L2AGLb"]/div')
# accept_cookies.click()

# time.sleep(1)

# search_bar = driver.find_element(By.XPATH, '//*[@id="APjFqb"]')
# search_bar.click()
# search_bar.send_keys('kace.com')
# search_bar.send_keys(Keys.ENTER)

# # search_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]')
# # search_button.click()

# time.sleep(2)

# page_source = driver.page_source

# driver.quit()

# soup = BeautifulSoup(page_source, "html.parser")


