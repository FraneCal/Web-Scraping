#---------------------------------- STARTING TEMPLATE WHEN SCRAPING USING BEAUTIFUL SOUP ----------------------------------#

from bs4 import BeautifulSoup
import requests


URL = "ENTER URL"

# FIND YOUR HEADER INFO HERE: https://myhttpheader.com/
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

response = requests.get(URL, headers=header)
response.raise_for_status()  

web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')

# START SCRAPING :)
