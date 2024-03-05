import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures
import pandas as pd

def fetch_event(link):
    response = requests.get(link)
    response.raise_for_status()
    return response.text

def scrape_event(link, unique_links, data):
    html = fetch_event(link)
    event_soup = BeautifulSoup(html, 'html.parser')
    event_name = event_soup.find('h1', class_='event-title css-0').getText()
    date_and_time = event_soup.find('span', class_='date-info__full-datetime').getText()
    data.append({'Event Name': event_name, 'Date and Time': date_and_time})

def main():
    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Calculate the end date (current date + 7 days)
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    # Construct the URL with dynamic start and end dates
    URL = f"https://www.eventbrite.com/d/canada--toronto/all-events/?page=1&start_date={current_date}&end_date={end_date}"

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    }

    response = requests.get(URL, headers=header)
    response.raise_for_status()
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html.parser')
    containers = soup.find_all('section', class_='event-card-details')

    # Use a set to store unique links
    unique_links = set()

    for container in containers:
        link = container.find('a', class_='event-card-link').get('href')
        unique_links.add(link)

    # Create an empty list to store the scraped data
    scraped_data = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrape_event, unique_links, [unique_links]*len(unique_links), [scraped_data]*len(unique_links))

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(scraped_data)

    # Save the DataFrame to an Excel file
    df.to_excel('scraped_events.xlsx', index=False)

if __name__ == "__main__":
    main()
