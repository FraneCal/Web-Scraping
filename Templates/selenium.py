#---------------------------------- STARTING TEMPLATE WHEN SCRAPING USING BEAUTIFUL SOUP AND SELENIUM (e.g. WHEN THE PAGE IS DYNAMIC) ----------------------------------#

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = "ENTER URL"

driver = webdriver.Chrome()
driver.get(URL)

page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, "html.parser")

# START SCRAPING :)
