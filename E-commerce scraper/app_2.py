'''
Remember to replace 'your_access_key', 'your_secret_key', 'your_associate_tag', and 'your_region' 
with your actual credentials. Also, you may need to handle pagination if there are more than 10 results. 
Adjust the code based on the response format of the API.
'''

from flask import Flask, render_template, request, session, redirect, url_for, flash
from bs4 import BeautifulSoup
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
        # ... rest of your code ...

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle the form submission (you can add your logic here)
        flash('Form submitted successfully!', 'success')
    return render_template('contact.html')

@app.route('/delete_results', methods=['POST'])
def delete_results():
    # Clear the stored results in the session
    session.pop('results', None)
    session.pop('product_name', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
