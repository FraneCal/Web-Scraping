from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import random
import time
import pandas as pd

URL = "https://www.oficinaempleo.com/buscar/ofertas/cloud-engineer"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    # Add other user agents as needed
]

service = Service()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)
time.sleep(3)

scroll_speed = 2  # seconds
scroll_increment = 0
max_attempts = 30  # Set a maximum number of attempts to avoid an infinite loop

while max_attempts > 0:
    current_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
    driver.execute_script(f"window.scrollTo(0, {current_height});")
    time.sleep(scroll_speed)

    new_height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

    if new_height == current_height:
        # No more dynamic content to load
        break

    max_attempts -= 1

time.sleep(2)

page_source = driver.page_source
driver.quit()

soup = BeautifulSoup(page_source, "html.parser")

# Initialize data lists
job_titles = []
date_posted_list = []
company_names = []
locations = []
sources = []

boxes = soup.find_all("div", class_="row col-dsk")
for box in boxes:
    job_link = box.find('h3').find('a')
    if job_link:
        job_title = job_link.get("title", "Job title not found")
        if any(keyword in job_title.lower() for keyword in ["cloud", "devops", "site", "reliability"]):
            date_posted = box.find("span", class_="result-hover-false").text.strip()
            company_name = soup.find('div', class_='col-sm-2 search-results-item-loc col-dsk').find('span').getText(strip=True)
            location = soup.find('div', class_='col-sm-2 search-results-item-loc col-dsk').find('a').getText()

            # Append data to lists
            job_titles.append(job_title)
            date_posted_list.append(date_posted)
            company_names.append(company_name)
            locations.append(location)
            sources.append("https://www.oficinaempleo.com")

# Create a DataFrame
data = {
    "Job Title": job_titles,
    "Date Posted": date_posted_list,
    "Company Name": company_names,
    "Location": locations,
    "Source": sources,
}

df = pd.DataFrame(data)

# Save to Excel
df.to_excel("officina_empleo_filtered.xlsx", index=False)
