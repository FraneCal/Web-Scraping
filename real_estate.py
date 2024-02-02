from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import requests
import random
import time

URL = "https://www.realestate.com.au/buy/list-1"

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Accept-Language": "en-US,en;q=0.9,hr;q=0.8"
}

max_retries = 5  # You can adjust the number of retries
retry_delay = 5  # You can adjust the delay between retries

for attempt in range(max_retries):
    try:
        response = requests.get(URL, headers=header)
        response.raise_for_status()
        break  # Break out of the loop if the request is successful
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 429:
            print(f"Received 429. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            raise  # Raise an exception for other HTTP errors 

web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')

# user_agents = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/94.0.992.47 Safari/537.36 Edg/94.0.992.47",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Android 11; Mobile; rv:93.0) Gecko/93.0 Firefox/93.0",
# ]
# service = Service()
# options = Options()
# options.add_argument(f"user-agent={random.choice(user_agents)}")
# driver = webdriver.Chrome(service=service, options=options)
# driver.get(URL)
# time.sleep(10) 
# web_page = driver.page_source
# soup = BeautifulSoup(web_page, 'html.parser')
# driver.quit()


adresses = soup.find_all('h2', class_='residential-card__address-heading')
links = soup.find_all('a', class_='details-link residential-card__details-link')
information = soup.find_all('div', class_='Inline__InlineContainer-sc-lf7x8d-0 iuOPWU residential-card__primary')

for info in information:
    print(info.text.strip())

for adress, link in zip(adresses, links):
    print(adress.text.strip())
    print(link.get('href'))
