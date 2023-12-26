from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
import random

URL = "https://coinmarketcap.com/"

driver = webdriver.Chrome()
driver.get(URL)
time.sleep(4)

scroll_increment = 0
while scroll_increment < 1000:
    driver.execute_script(f"window.scrollTo(0, {scroll_increment * 10});")
    time.sleep(random.uniform(1, 2))
    scroll_increment += 100

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Extract header information
header_columns = soup.select('thead th')
header_data = [col.get_text(strip=True) for col in header_columns]

# Find the table body
table_body = soup.find("div", class_="sc-feda9013-2 dxcftz").find('tbody')

if table_body:
    # Initialize data list to store rows
    data = []
    
    # Iterate through rows in the table body
    for row in table_body.find_all('tr'):
        # Extract data from each column in the row
        columns = row.find_all(['td', 'th'])
        row_data = [col.get_text(strip=True) for col in columns]

        # Skip the first item in row_data (first column)
        row_data = row_data[1:]

        # Append row data to the list
        data.append(row_data)
    
    # Create a DataFrame from the header and data
    df = pd.DataFrame(data, columns=header_data[1:])

    # Save DataFrame to an Excel file
    with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
        print("Data saved to 'output.xlsx'")
else:
    print("Table not found.")
