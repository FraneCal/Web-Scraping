from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials


URL = "https://www.zillow.com/san-francisco-ca/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22San%20Francisco%2C%20CA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-122.52499667529297%2C%22east%22%3A-122.34166232470703%2C%22south%22%3A37.662044543503555%2C%22north%22%3A37.88836615784793%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20330%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22days%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D"

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
while scroll_increment < 500: 
    driver.execute_script(f"window.scrollTo(0, {scroll_increment * 10});")
    time.sleep(random.uniform(1, 2))
    scroll_increment += 50

web_page = driver.page_source
driver.quit()

soup = BeautifulSoup(web_page, 'lxml')

# ---------------- Prices ---------------- #
prices = soup.find_all("span", class_="PropertyCardWrapper__StyledPriceLine-srp__sc-16e8gqd-1 iMKTKr")
prices_list = [price.getText().split()[0] for price in prices if price.getText().startswith('$')]
#print(prices_list)

# ---------------- Bedrooms and bathrooms ---------------- #
quantities = soup.find_all("ul", class_="StyledPropertyCardHomeDetailsList-c11n-8-84-3__sc-1xvdaej-0 eYPFID")
quantity_list = [
    " ".join(
        q.getText(strip=True)
        for q in quantity.select("li")
        if not q.getText().startswith("--")
    )
    for quantity in quantities
]
#print(quantity_list)

# ---------------- Addresses ---------------- #
adresses = soup.find_all("address")
adresses_list = [adress.getText() for adress in adresses]
#print(adresses_list)

# ---------------- LINKS ---------------- #
links = soup.find_all("a", class_="StyledPropertyCardDataArea-c11n-8-84-3__sc-yipmu-0 jnnxAW property-card-link")
links_clean = [link.get("href") for link in links]
#print(links_clean)


# ---------------- MERGED LIST OF EVERYTHING ---------------- #
merged_list = [[prices_list[i], quantity_list[i], adresses_list[i], links_clean[i]] for i in range(len(prices_list))]


# ---------------- WRITING TO GOOGLE SHEETS ---------------- #
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open("PythonSheets").sheet1

for row_number in range(len(prices_list)):
    if row_number < len(prices_list):
        sheet.insert_row([prices_list[row_number], quantity_list[row_number], adresses_list [row_number], links_clean[row_number]], 2+row_number)
      
