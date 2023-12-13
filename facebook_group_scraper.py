from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

URL = "https://www.facebook.com/groups/463378418478705/members"

driver = webdriver.Chrome()
driver.get(URL)

time.sleep(15)
handle_cookies = driver.find_element(By.XPATH, '//*[@id="u_0_j_LQ"]')
handle_cookies.click()
time.sleep(1)

email = driver.find_element(By.XPATH, '//*[@id="email"]')
email.click()
email.send_keys('fcalus00@fesb.hr')

password = driver.find_element(By.XPATH, '//*[@id="pass"]')
password.click()
password.send_keys('In71948N')

log_in = driver.find_element(By.XPATH, '//*[@id="loginbutton"]')
log_in.click()

time.sleep(5)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, "lxml")

name = soup.find("a", class_="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f")

print(name)
