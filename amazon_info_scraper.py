from bs4 import BeautifulSoup
import requests
import concurrent.futures

header = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
  "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_page(page_num):
    URL = f"https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&qid=1702226389&sprefix=laptop%2Caps%2C572&ref=sr_pg_{page_num}"
    
    response = requests.get(URL, headers=header)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'lxml')

    image_boxes = soup.find_all("div", class_="s-product-image-container aok-relative s-text-center s-image-overlay-grey puis-image-overlay-grey s-padding-left-small s-padding-right-small puis-flex-expand-height puis puis-v25h6k2ialgxcx2aefs5gqn1u23")
    boxes = soup.find_all("div", class_="puisg-col puisg-col-4-of-12 puisg-col-8-of-16 puisg-col-12-of-20 puisg-col-12-of-24 puis-list-col-right")

    local_name_list = []
    local_price_list = []
    local_number_of_reviews_list = []
    local_images_list = []

    for box in boxes:
        name = box.find("span", class_="a-size-medium a-color-base a-text-normal").getText()
        price = box.find("span", class_="a-offscreen").getText()
        number_of_reviews = box.find("span", class_="a-size-base s-underline-text").getText()

        local_name_list.append(name)
        local_price_list.append(price)
        local_number_of_reviews_list.append(number_of_reviews)

    for image_box in image_boxes:
        images = image_box.find("img", class_="s-image").get('src')
        local_images_list.append(images)

    return local_name_list, local_price_list, local_number_of_reviews_list, local_images_list

# Variables to store aggregated results
name_list = []
price_list = []
number_of_reviews_list = []
images_list = []

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(scrape_page, range(1, 20))

for result in results:
    name_list.extend(result[0])
    price_list.extend(result[1])
    number_of_reviews_list.extend(result[2])
    images_list.extend(result[3])

# Output results
print(len(name_list))
print(len(price_list))
print(len(number_of_reviews_list))
print(len(images_list))









# from bs4 import BeautifulSoup
# import requests

# header = {
#   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
#   "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
# }

# # Variables to store aggregated results
# name_list = []
# price_list = []
# number_of_reviews_list = []
# images_list = []

# for page_num in range(1, 20):
#     URL = f"https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&qid=1702226389&sprefix=laptop%2Caps%2C572&ref=sr_pg_{page_num}"

#     response = requests.get(URL, headers=header)
#     web_page = response.text
#     soup = BeautifulSoup(web_page, 'lxml')

#     image_boxes = soup.find_all("div", class_="s-product-image-container aok-relative s-text-center s-image-overlay-grey puis-image-overlay-grey s-padding-left-small s-padding-right-small puis-flex-expand-height puis puis-v25h6k2ialgxcx2aefs5gqn1u23")
#     boxes = soup.find_all("div", class_="puisg-col puisg-col-4-of-12 puisg-col-8-of-16 puisg-col-12-of-20 puisg-col-12-of-24 puis-list-col-right")

#     for box in boxes:
#         name = box.find("span", class_="a-size-medium a-color-base a-text-normal").getText()
#         price = box.find("span", class_="a-offscreen").getText()
#         number_of_reviews = box.find("span", class_="a-size-base s-underline-text").getText()

#         name_list.append(name)
#         price_list.append(price)
#         number_of_reviews_list.append(number_of_reviews)

#     for image_box in image_boxes:
#         images = image_box.find("img", class_="s-image").get('src')
#         images_list.append(images)

# # Output results
# print(len(name_list))
# print(len(price_list))
# print(len(number_of_reviews_list))
# print(len(images_list))
