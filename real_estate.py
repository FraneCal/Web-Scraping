from bs4 import BeautifulSoup
import requests

URL = "https://www.realestate.com.au/buy/list-1"

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Accept-Language": "en-US,en;q=0.9,hr;q=0.8"
}

response = requests.get(URL, headers=header)
response.raise_for_status()  

web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')

adresses = soup.find_all('h2', class_='residential-card__address-heading')
information = soup.find('div', class_='piped-content__outer').text.strip()
print(information)

for adress in adresses:
    print(adress.text.strip())
    # print(info.text.strip())
