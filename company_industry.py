import requests

url = 'https://api.thecompaniesapi.com/v1/companies/similar'
headers = {'Authorization': 'Basic 3C69nnR1'}
param = {'domains[]': 'kace.com'}

try:
    response = requests.get(url, headers=headers , params=param)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    data = response.json()
    main_industry = data['companies'][0]['industryMain']
    industries = data['companies'][0]['industries']
    #print(data)
except requests.exceptions.HTTPError as errh:
    print("HTTP Error:", errh)
except requests.exceptions.RequestException as err:
    print("Request Error:", err)

print(main_industry)
print(industries)




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


