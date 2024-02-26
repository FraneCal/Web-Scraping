from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

URL = "https://www.zillow.com/los-angeles-ca/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-119.18214875976562%2C%22east%22%3A-117.64131624023437%2C%22south%22%3A33.50217331361113%2C%22north%22%3A34.536814338825764%7D%2C%22usersSearchTerm%22%3A%22Los%20Angeles%2C%20CA%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12447%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A2400%7D%2C%22price%22%3A%7B%22max%22%3A468764%7D%7D%2C%22isListVisible%22%3Atrue%7D"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
]

service = Service()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)
time.sleep(random.uniform(3, 5))

scroll_increment = 0
while scroll_increment < 600: 
    driver.execute_script(f"window.scrollTo(0, {scroll_increment * 10});")
    time.sleep(random.uniform(1, 2))
    scroll_increment += 100

web_page = driver.page_source

next_page = driver.find_element(By.XPATH, '//*[@id="grid-search-results"]/div[2]/nav/ul/li[10]/a')
next_page.click()

time.sleep(5)

driver.quit()

soup = BeautifulSoup(web_page, 'lxml')

all_data = {
        'Price': [],
        'Address': [],
        'Link': [],
    }

# ---------------- Prices ---------------- #
prices = soup.find_all("span", class_="PropertyCardWrapper__StyledPriceLine-srp__sc-16e8gqd-1 iMKTKr")
prices_list = [price.getText().split()[0] for price in prices if price.getText().startswith('$')]
#print(prices_list)

# ---------------- Addresses ---------------- #
adresses = soup.find_all("address")
adresses_list = [adress.getText() for adress in adresses]
#print(adresses_list)

# ---------------- LINKS ---------------- #
links = soup.find_all("a", class_="StyledPropertyCardDataArea-c11n-8-84-3__sc-yipmu-0 jnnxAW property-card-link")
links_clean = []
for link in links:
  actual_link = link.get("href")
  if actual_link.startswith("https://www.zillow.com"):
    links_clean.append(actual_link)
  else:
    links_clean.append("https://www.zillow.com" + actual_link)
#print(links_clean)

all_data['Price'].extend(prices_list)
all_data['Address'].extend(adresses_list)
all_data['Link'].extend(links_clean)

df = pd.DataFrame(all_data)
df.to_excel("zillow_data.xlsx", index=False)
df['Price'] = df['Price'].str.replace(r"\+|\/mo", "", regex=True)
df.to_excel("zillow_data.xlsx", index=False)
