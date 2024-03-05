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




# ---------------------------- THIS PART SCRAPES ALL OF THE PAGES ---------------------------- #

# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta
# import concurrent.futures
# import pandas as pd
# import time

# def fetch_event(link):
#     response = requests.get(link)
#     if response.status_code == 429:
#         # If 429 error, implement exponential backoff
#         wait_time = 2 ** response.headers.get('Retry-After', 3)
#         print(f"Received 429 error. Retrying after {wait_time} seconds.")
#         time.sleep(wait_time)
#         return fetch_event(link)
#     response.raise_for_status()
#     return response.text

# def scrape_event(link):
#     html = fetch_event(link)
#     event_soup = BeautifulSoup(html, 'html.parser')
#     event_name = event_soup.find('h1', class_='event-title css-0').getText()
#     date_and_time = event_soup.find('span', class_='date-info__full-datetime').getText()
#     return {"Event Name": event_name, "Date and Time": date_and_time}

# def get_links_from_page(page_url):
#     response = requests.get(page_url)
#     response.raise_for_status()
#     page_soup = BeautifulSoup(response.text, 'html.parser')
#     containers = page_soup.find_all('section', class_='event-card-details')
#     links = [container.find('a', class_='event-card-link').get('href') for container in containers]
#     return links

# def main():
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

#     header = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
#         "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
#     }

#     scraped_data = []

#     for page_number in range(1, 10):
#         URL = f"https://www.eventbrite.com/d/canada--toronto/all-events/?page={page_number}&start_date={current_date}&end_date={end_date}"
#         links = get_links_from_page(URL)

#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             results = list(executor.map(scrape_event, links))
#             scraped_data.extend(results)

#         # Add a delay to avoid rate limiting
#         time.sleep(2)  # You can adjust the delay time as needed

#     # Create a DataFrame to remove duplicates
#     df = pd.DataFrame(scraped_data).drop_duplicates()

#     # Save all scraped data to one Excel file
#     df.to_excel("events_data_combined.xlsx", index=False)
#     print("All data saved to 'events_data_combined.xlsx'")

# if __name__ == "__main__":
#     main()
