from bs4 import BeautifulSoup
import requests
import concurrent.futures

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def scrape_page(product_name, page_num):
    try:
        URL = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}&crid=288NMI7Z5E2WR&qid=1702226389&sprefix={product_name.replace(' ', '%2C')}%2Caps%2C572&ref=sr_pg_{page_num}"

        response = requests.get(URL, headers=header)
        response.raise_for_status()

        web_page = response.text
        soup = BeautifulSoup(web_page, 'lxml')

        result_container = soup.find("div", class_="s-main-slot")

        if result_container:
            boxes = result_container.find_all("div", class_="s-result-item")
        else:
            print(f"No search results found on page {page_num}")
            return [], []

        local_name_list = []
        local_price_list = []
        local_image_list = []

        for box in boxes:
            try:
                name_elem = box.find("span", class_="a-size-medium a-color-base a-text-normal")
                price_elem = box.find("span", class_="a-offscreen")
                image_elem = box.find("img", class_="s-image")

                if name_elem and price_elem and image_elem:
                    name = name_elem.getText()
                    price = price_elem.getText()
                    image_url = image_elem['src']

                    local_name_list.append(name)
                    local_price_list.append(price)
                    local_image_list.append(image_url)
                    print(f"Product: {name}\nPrice: {price}\nImage URL: {image_url}\n{'=' * 30}")

            except AttributeError as e:
                print(f"Error extracting data from box on page {page_num}: {e}")
                continue

        return local_name_list, local_price_list, local_image_list

    except requests.exceptions.RequestException as e:
        print(f"Error scraping page {page_num}: {e}")
        return [], [], []  # Return empty lists in case of an error

if __name__ == "__main__":
    product_name = input("Enter the name of the product you want to search for on Amazon: ")

    name_list = []
    price_list = []
    image_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(scrape_page, [product_name] * 18, range(1, 19))

    for result in results:
        name_list.extend(result[0])
        price_list.extend(result[1])
        image_list.extend(result[2])

    if not name_list:
        print(f"No search results found for '{product_name}'.")
    else:
        print("\nSearch results:")
        for name, price, image_url in zip(name_list, price_list, image_list):
            print(f"Product: {name}\nPrice: {price}\nImage URL: {image_url}\n{'=' * 30}")
