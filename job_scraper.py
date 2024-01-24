#https://www.youtube.com/watch?v=eN_3d4JrL_w

import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def get_url(position, location):
    template = "https://de.indeed.com/jobs?q={}&l={}"
    url = template.format(position, location)
    return url

url = get_url('cloud enginner', 'germany')

driver = webdriver.Chrome()
driver.get(url)
time.sleep(2)

cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
cookies.click()

time.sleep(1)

page_source = driver.page_source
driver.quit()
soup = BeautifulSoup(page_source, "html.parser")

cards = soup.find('li', class_='css-5lfssm eu4oa1w0').getText()
print(cards)
