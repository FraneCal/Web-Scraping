import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve

def download_images_from_website(url, save_folder, keyword, max_images=10):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    count = 0
    for img_tag in img_tags:
        img_url = img_tag.get('src')
        if img_url:
            img_url = urljoin(url, img_url)
            img_name = f"{keyword}_{count}.jpg"
            img_path = os.path.join(save_folder, img_name)
            urlretrieve(img_url, img_path)
            count += 1

            if count >= max_images:
                break

def scrape_images_from_multiple_websites(urls, save_folder, keyword, max_images=10):
    for url in urls:
        download_images_from_website(url, save_folder, keyword, max_images)

if __name__ == "__main__":
    # Write the website you want to scrape images from
    websites = [
        "https://www.google.com/search?sca_esv=583768629&sxsrf=AM9HkKk0ujYpSGwNgtsEKz9Cj80cCnKoUA:1700396993168&q=cats&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjm_YO2iNCCAxV0VEEAHcGtDgYQ0pQJegQIEBAB&biw=1920&bih=969&dpr=1",
    ]

    save_folder = "image_dataset"  # Folder to save downloaded images
    keyword = "cats"  # A keyword to include in the image filenames
    max_images = 30  # Maximum number of images to download from each website

    scrape_images_from_multiple_websites(websites, save_folder, keyword, max_images)
