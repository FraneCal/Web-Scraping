from bs4 import BeautifulSoup
import requests
import threading
import json
import re
 
URL = "https://felix.com.pa/search?type=product&q=*"
header = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Accept-Language": "en-US,en;q=0.9,hr;q=0.8"
}
 
response = requests.get(URL, headers=header)
response.raise_for_status()
web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')
products = soup.find_all('div', class_='product-wrap')
links = [f"https://felix.com.pa{product.find('a').get('href')}" for product in products]
 
data = {
    "Image link": [],
    "Title": [],
    "Price": [],
    "Variables": {
        "Color": [],
        "Size": [],
    },
    "Description": [],
}
 
# Lock to ensure safe access to shared data
lock = threading.Lock()
 
def clean_title(title):
    cleaned_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    return cleaned_title.strip()
 
def scrape_and_store(link):
    response = requests.get(link, headers=header)
    response.raise_for_status()
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')
    
    with lock:
        # Title
        title = soup.find('h1', class_='product_name title').getText()
        cleaned_title = clean_title(title)
        data["Title"].append(cleaned_title)
 
        # Image link
        image_link = soup.find('a', class_='product-gallery__link').get('href')
        data['Image link'].append(image_link)
 
        # Price
        price = soup.find('div', class_='product-block--price').find('span', class_='money').getText()
        data['Price'].append(price)
 
        # Description
        description = soup.find('div', id='view-more_description').find('p').getText()
        data['Description'].append(description)
 
        # Variables (size, color, style/version/edition)
        color_element = soup.find('div', class_='product-block--form').find('span')
        color = color_element.getText().split(":")[1].strip() if color_element else None
        data['Variables']['Color'].append(color)
 
        # Size
        size_element = soup.find('div', class_='product-block--form').find('span', class_='attr-title-hover')
        print(size_element)
        size = size_element.getText().strip() if size_element else None
        data['Variables']['Size'].append(size)
 
def main():
    threads = []
 
    for link in links:
        thread = threading.Thread(target=scrape_and_store, args=(link,))
        threads.append(thread)
        thread.start()
 
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
 
    # Save data to JSON file
    with open('scraped_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)
 
if __name__ == "__main__":
    main()
