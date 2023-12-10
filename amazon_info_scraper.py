from bs4 import BeautifulSoup
import requests
import concurrent.futures
import csv
import pandas as pd

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_page(page_num):
    try:
        URL = f"https://www.amazon.com/s?k=laptop&crid=288NMI7Z5E2WR&qid=1702226389&sprefix=laptop%2Caps%2C572&ref=sr_pg_{page_num}"

        response = requests.get(URL, headers=header)
        response.raise_for_status()  # Raise an HTTPError for bad responses

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

    except requests.exceptions.RequestException as e:
        print(f"Error scraping page {page_num}: {e}")
        return [], [], [], []  # Return empty lists in case of an error

# Variables to store aggregated results
name_list = []
price_list = []
number_of_reviews_list = []
images_list = []

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(scrape_page, range(1, 22))

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






# concurrent.futures.ThreadPoolExecutor(): This line creates a thread pool executor, which is a part of the concurrent.futures module in Python. 
# A thread pool is a group of pre-initialized threads that are ready to execute tasks concurrently.

# with ... as executor:: The with statement is used here to create a context manager for the thread pool executor. It ensures proper resource management and cleanup when the block of code inside the with statement is exited.

# executor.map(scrape_page, range(1, 20)): The map method of the executor is used to apply the scrape_page function to each element in the iterable range(1, 20) concurrently. It divides the iterable into chunks and 
#executes the function on each chunk using the threads from the thread pool.

# scrape_page: This is the function that performs the scraping logic for a given page number.

# range(1, 20): It generates an iterable with page numbers from 1 to 19 (inclusive).

# executor.map returns an iterator of results from applying the function to each element in the iterable.

# The results are stored in the results variable.








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
