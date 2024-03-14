import requests
import sqlite3
import smtplib

# Function to create a SQLite database and table if they don't exist
def create_database():
    conn = sqlite3.connect('ethereum_prices.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ethereum_prices
                 (id INTEGER PRIMARY KEY, price REAL)''')
    conn.commit()
    conn.close()

# Function to get the latest Ethereum price from the database
def get_latest_price():
    conn = sqlite3.connect('ethereum_prices.db')
    c = conn.cursor()
    c.execute('SELECT price FROM ethereum_prices ORDER BY id DESC LIMIT 1')
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# Function to update the database with the latest Ethereum price
def update_database(price):
    conn = sqlite3.connect('ethereum_prices.db')
    c = conn.cursor()
    c.execute('INSERT INTO ethereum_prices (price) VALUES (?)', (price,))
    conn.commit()
    conn.close()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'symbol': 'ETH'
}
headers = {
  'X-CMC_PRO_API_KEY': '56f27124-a21d-4d1e-9080-f56b7e817022'
}

try:
    # Create or connect to the database
    create_database()

    # Fetch the latest Ethereum price from the database
    old_price = get_latest_price()

    # Fetch the latest Ethereum price from the API
    response = requests.get(url, params=parameters, headers=headers)
    data = response.json()
    new_price = float(data['data']['ETH']['quote']['USD']['price'])

    # Update the database with the new price
    update_database(new_price)

    # Compare the prices and print the appropriate message
    if old_price:
        price_diff = new_price - old_price
        price_change_percentage = (price_diff / old_price) * 100
        if price_change_percentage <= -5:
            print("Ethereum price has fallen by more than 5%.")
        elif price_change_percentage >= 5:
            print("Ethereum price has risen by more than 5%.")
        elif price_change_percentage <= 1 or price_change_percentage >= -1:
            print(f"Etherium price changed less than 1%. The current price is: {new_price}")

            my_email = 'franecalusic94@gmail.com'
            password = 'jmyxbqpbrzlteway'

            with smtplib.SMTP('smtp.gmail.com') as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email,
                                    to_addrs='fcalus00@fesb.hr',
                                    msg=f'Subject:Etherium price\n\n Etherium price changed less than 1%. The current price is: {new_price}')
                
except Exception as e:
    print("Error:", e)
