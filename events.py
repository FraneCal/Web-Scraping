from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

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

# Event name
names = soup.find_all('h2', class_='Typography_root__487rx #3a3247 Typography_body-lg__487rx event-card__clamp-line--two Typography_align-match-parent__487rx')
names_set = set()
for name in names:
    names_set.add(name.getText())

names_list = list(names_set)

# Event date and time
dates_and_times = soup.find_all('p', class_='Typography_root__487rx #585163 Typography_body-md__487rx event-card__clamp-line--one Typography_align-match-parent__487rx')

filtered_dates_and_times = []

for date_and_time in dates_and_times:
    text = date_and_time.getText().strip()
    if 'at' in text and (text.endswith('AM') or text.endswith('PM')):
        filtered_dates_and_times.append(text)

for name, date_and_time in zip(names_list, filtered_dates_and_times):
    print(f"Event Name: {name}\tEvent Date and Time: {date_and_time}")
