from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import random
import time


URL = "https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&sprefix=laptop%2Caps%2C572&ref=nb_sb_noss_1"

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
time.sleep(random.uniform(3, 4))

web_page = driver.page_source
driver.quit()

soup = BeautifulSoup(web_page, 'lxml')


image_boxes = soup.find_all("div", class_="s-product-image-container aok-relative s-text-center s-image-overlay-grey puis-image-overlay-grey s-padding-left-small s-padding-right-small puis-flex-expand-height puis puis-v25h6k2ialgxcx2aefs5gqn1u23")
boxes = soup.find_all("div", class_="puisg-col puisg-col-4-of-12 puisg-col-8-of-16 puisg-col-12-of-20 puisg-col-12-of-24 puis-list-col-right")

name_list = []
price_list = []
number_of_reviews_list = []
images_list = []

for box in boxes:
    name = box.find("span", class_="a-size-medium a-color-base a-text-normal").getText()
    price = box.find("span", class_="a-offscreen").getText()
    number_of_reviews = box.find("span", class_="a-size-base s-underline-text").getText()

    name_list.append(name)
    price_list.append(price)
    number_of_reviews_list.append(number_of_reviews)

    
for image_box in image_boxes:
    images = image_box.find("img", class_="s-image").get('src')
    images_list.append(images)


print(len(name_list))
print(len(price_list))
print(len(number_of_reviews_list))
print(len(images_list))
