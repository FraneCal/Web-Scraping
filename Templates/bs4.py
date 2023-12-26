#---------------------------------- STARTING TEMPLATE WHEN SCRAPING USING BEAUTIFUL SOUP ----------------------------------#

from bs4 import BeautifulSoup
import requests


URL = "ENTER URL"

# FIND YOUR HEADER INFO HERE: https://myhttpheader.com/
header = {
    "User-Agent": "YOUR USER AGENT",
    "Accept-Language": "YOUR ACCEPT LANGUAGE"
}

response = requests.get(URL, headers=header)
response.raise_for_status()  

web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')

# START SCRAPING :)
