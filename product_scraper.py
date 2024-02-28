from bs4 import BeautifulSoup
import requests
import threading
import json
import re

BASE_URL = "https://felix.com.pa/search"
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Accept-Language": "en-US,en;q=0.9,hr;q=0.8"
}

# Function to get links from a specific page
def get_links(page_number):
    url = f"{BASE_URL}?page={page_number}&q=%2A&type=product"
    response = requests.get(url, headers=header)
    response.raise_for_status()
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')
    products = soup.find_all('div', class_='product-wrap')
    return [f"https://felix.com.pa{product.find('a').get('href')}" for product in products]

# Lock to ensure safe access to shared data
lock = threading.Lock()

# Shared data list
data = []

def clean_title(title):
    cleaned_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return cleaned_title.strip()

def scrape_and_store(link, counter):
    response = requests.get(link, headers=header)
    response.raise_for_status()
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')

    product_data = {
        "Title": None,
        "Image link": None,
        "Price": None,
        "Color / Size": None,
        "Description": None,
    }

    title = soup.find('h1', class_='product_name title').getText()
    cleaned_title = clean_title(title)
    product_data["Title"] = cleaned_title

    image_link = soup.find('a', class_='product-gallery__link').get('href')
    product_data['Image link'] = image_link

    price = soup.find('div', class_='product-block--price').find('span', class_='money').getText()
    product_data['Price'] = price

    description = soup.find('div', id='view-more_description').find('p').getText()
    product_data['Description'] = description

    size_elements = soup.find('div', class_='product-block--form').find('select', class_='variant-selection__variants')
    if size_elements:
        size_options = [option.text.strip().rsplit(' - ', 1)[0] for option in size_elements.find_all('option')][1:]
        product_data['Color / Size'] = size_options

    with lock:
        data.append(product_data)

def scrape_and_store_all_pages(start_page, end_page):
    threads = []

    for page in range(start_page, end_page + 1):
        links = get_links(page)
        for i, link in enumerate(links):
            thread = threading.Thread(target=scrape_and_store, args=(link, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete before moving to the next page
        for thread in threads:
            thread.join()

    # Save data to JSON file
    with open('scraped_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)

if __name__ == "__main__":
    scrape_and_store_all_pages(1, 100)

# import json

# def count_dicts(json_data):
#     count = 0
#     if isinstance(json_data, dict):
#         count += 1
#         for value in json_data.values():
#             count += count_dicts(value)
#     elif isinstance(json_data, list):
#         for item in json_data:
#             count += count_dicts(item)
#     return count

# if __name__ == "__main__":
#     # Load JSON file
#     with open('scraped_data.json', 'r') as json_file:
#         json_data = json.load(json_file)

#     # Count dictionaries
#     dictionaries_count = count_dicts(json_data)

#     print(f"Number of dictionaries in the JSON file: {dictionaries_count}")
