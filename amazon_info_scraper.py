from bs4 import BeautifulSoup
import requests
import concurrent.futures
import csv
import pandas as pd
import time

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_page(page_num):
    try:
        URL = f"https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&qid=1702226389&sprefix=laptop%2Caps%2C572&ref=sr_pg_{page_num}"

        response = requests.get(URL, headers=header)
        response.raise_for_status()  

        web_page = response.text
        soup = BeautifulSoup(web_page, 'lxml')

        image_boxes = soup.find_all("div", class_="s-product-image-container aok-relative s-text-center s-image-overlay-grey puis-image-overlay-grey s-padding-left-small s-padding-right-small puis-flex-expand-height puis puis-v25h6k2ialgxcx2aefs5gqn1u23")
        boxes = soup.find_all("div", class_="puisg-col puisg-col-4-of-12 puisg-col-8-of-16 puisg-col-12-of-20 puisg-col-12-of-24 puis-list-col-right")

        local_name_list = []
        local_price_list = []
        local_number_of_reviews_list = []
        local_images_list = []

        for box in boxes:
            try:
                name = box.find("span", class_="a-size-medium a-color-base a-text-normal").getText()
                price = box.find("span", class_="a-offscreen").getText()
                number_of_reviews = box.find("span", class_="a-size-base s-underline-text").getText()

                local_name_list.append(name)
                local_price_list.append(price)
                local_number_of_reviews_list.append(number_of_reviews)

            except AttributeError as e:
                print(f"Error extracting data from box on page {page_num}: {e}")
                continue  

        for image_box in image_boxes:
            try:
                images = image_box.find("img", class_="s-image").get('src')
                local_images_list.append(images)

            except AttributeError as e:
                print(f"Error extracting image data on page {page_num}: {e}")
                continue  

        return local_name_list, local_price_list, local_number_of_reviews_list, local_images_list

    except requests.exceptions.RequestException as e:
        print(f"Error scraping page {page_num}: {e}")
        return [], [], [], []  # Return empty lists in case of an error


name_list = []
price_list = []
number_of_reviews_list = []
images_list = []

delay_between_requests = 1

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(scrape_page, range(1, 19))
    time.sleep(delay_between_requests)

for result in results:
    name_list.extend(result[0])
    price_list.extend(result[1])
    number_of_reviews_list.extend(result[2])
    images_list.extend(result[3])

merged_list = [[name_list[i], price_list[i], number_of_reviews_list[i], images_list[i]] for i in range(len(name_list))]

headers = ['Name', 'Price', 'Number of Reviews', 'Images']
data = [headers] + merged_list
csv_file_path = 'output.csv'

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f'The data has been successfully saved to {csv_file_path}')

df = pd.DataFrame(merged_list, columns=['Name', 'Price', 'Number of Reviews', 'Images'])

print(df)
