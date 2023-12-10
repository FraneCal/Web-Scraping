import requests
from bs4 import BeautifulSoup

# Create a session object
s = requests.Session()

# Set headers
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
})

URL = "https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&sprefix=laptop%2Caps%2C572&ref=nb_sb_noss_1"

# Use the session to get the page content
response = s.get(URL)

web_page = response.text

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
