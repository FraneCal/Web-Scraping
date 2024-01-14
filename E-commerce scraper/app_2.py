'''
Remember to replace 'your_access_key', 'your_secret_key', 'your_associate_tag', and 'your_region' 
with your actual credentials. Also, you may need to handle pagination if there are more than 10 results. 
Adjust the code based on the response format of the API.
'''

from flask import Flask, render_template, request, session, redirect, url_for, flash
from bs4 import BeautifulSoup
import requests
import concurrent.futures
import sqlite3
import boto3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

amazon_access_key = 'your_access_key'
amazon_secret_key = 'your_secret_key'
amazon_associate_tag = 'your_associate_tag'
region = 'your_region'  # e.g., 'us-east-1'

client = boto3.client(
    'product-advertising',
    aws_access_key_id=amazon_access_key,
    aws_secret_access_key=amazon_secret_key,
    region_name=region
)

conn = sqlite3.connect('amazon_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price TEXT,
        image_url TEXT,
        scraping_status TEXT
    )
''')
conn.commit()

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def search_amazon(product_name):
    response = client.search_items(
        Keywords=product_name,
        SearchIndex='All',
        ItemCount=10  # Adjust as needed
    )

    items = response['SearchResult']['Items']
    for item in items:
        title = item['ItemInfo']['Title']['DisplayValue']
        price = item.get('Offers', {}).get('SummarizedPrice', {}).get('DisplayAmount', 'N/A')
        print(f"Title: {title}, Price: {price}")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        search_amazon(product_name)

        try:
            URL = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
            response = requests.get(URL, headers=header)
            response.raise_for_status()
            web_page = response.text
            soup = BeautifulSoup(web_page, 'html.parser')

            name_list = []
            price_list = []
            image_list = []

            for box in soup.find_all("div", class_="s-result-item"):
                name_elem = box.find("span", class_="a-size-medium a-color-base a-text-normal")
                price_elem = box.find("span", class_="a-offscreen")
                image_elem = box.find("img", class_="s-image")

                if name_elem and price_elem and image_elem:
                    name = name_elem.get_text(strip=True)
                    price = price_elem.get_text(strip=True)
                    image_url = image_elem['src']

                    name_list.append(name)
                    price_list.append(price)
                    image_list.append(image_url)

            merged_list = list(zip(name_list, price_list, image_list))

            if not merged_list:
                return render_template('home.html', no_results=True, product_name=product_name)
            else:
                session['results'] = merged_list
                session['product_name'] = product_name

                return render_template('home.html', results=merged_list, product_name=product_name)

        except requests.exceptions.RequestException as e:
            print(f"Error scraping Amazon: {e}")
            return render_template('home.html', no_results=True, product_name=product_name)

    if 'results' in session:
        results = session['results']
        product_name = session['product_name']
        return render_template('home.html', results=results, product_name=product_name)

    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Form submitted successfully!', 'success')
    return render_template('contact.html')

@app.route('/delete_results', methods=['POST'])
def delete_results():
    session.pop('results', None)
    session.pop('product_name', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
