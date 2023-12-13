from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

driver = webdriver.Chrome()

URL = "https://www.flightradar24.com/data/aircraft/n230wp"
driver.get(URL)
time.sleep(3)

# Handling pop ups and log in
pop_up_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
pop_up_button.click()
time.sleep(1)

log_in_button = driver.find_element(By.XPATH, '//*[@id="auth-button"]/div')
log_in_button.click()
time.sleep(1)

email = driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-2"]/div/div/div/form/div[1]/div/input')
email.click()
email.send_keys('YOUR EMAIL')

password = driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-2"]/div/div/div/form/div[2]/div/input')
password.click()
password.send_keys('YOUR PASSWORD')

log_in_button = driver.find_element(By.XPATH, '//*[@id="headlessui-disclosure-panel-2"]/div/div/div/form/button')
log_in_button.click()
time.sleep(5)

try:
    # Adjust the number 50 to more if needed
    for _ in range(0, 50):
        # Scroll to the bottom of the page and click "Load more" button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        load_more_flights = driver.find_element(By.XPATH, '//*[@id="btn-load-earlier-flights"]')
        load_more_flights.click()
        time.sleep(1.5)
except:
    print('Buton for "Load more" not found. Exiting loop.')

time.sleep(2)

# Loading data and saving it to this varible
page_source = driver.page_source
driver.quit()

soup = BeautifulSoup(page_source, "lxml")

table = soup.find('table', {'id': 'tbl-datatable'})

# Check if the table is found
if table:
    # Initialize data list to store rows
    data = []
    
    # Iterate through rows in the table body
    for row in table.select('tbody tr'):
        # Extract data from each column in the row
        columns = row.find_all(['td', 'th'])
        row_data = [col.get_text(strip=True) for col in columns]
        
        # Append row data to the list
        data.append(row_data)
    
    # Create a DataFrame from the data
    df = pd.DataFrame(data[1:], columns=data[0])

    # Save DataFrame to an Excel file
    with pd.ExcelWriter("output_dirty.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
        print("Data saved to 'output.xlsx'")
else:
    print("Table not found.")
