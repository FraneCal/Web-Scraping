from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import random
import time
from googlesearch import search
from datetime import datetime, timedelta

def get_url(position):
    template = "https://de.indeed.com/jobs?q={}"
    url = template.format(position)
    return url

def parse_non_standard_date(date_str):
    try:
        if "Vor" in date_str:
            if ">" in date_str:
                days_ago = 31  # Assign a value greater than 30 if the exact number is not specified
            else:
                days_ago = int(date_str.split()[1])
            return (datetime.today() - timedelta(days=days_ago)).strftime("%d-%m-%Y")
    except ValueError:
        pass
    return "Invalid Date Format"

def get_company_url(company_name):
    try:
        search_query = f"{company_name} official website"
        search_results = search(search_query, pause=2)
        for result in search_results:
            return result
    except Exception as e:
        print(f"Error searching for {company_name} URL: {e}")
        return None

url = get_url('cloud engineer')

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
]

service = Service()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(service=service, options=options)
driver.get(url)

time.sleep(5)

# Handle cookies (assuming the cookie button has an id="onetrust-accept-btn-handler")
try:
    cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
    cookies.click()
except Exception as e:
    print(f"Error clicking on cookies button: {e}")

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

page_source = driver.page_source
driver.quit()
soup = BeautifulSoup(page_source, "html.parser")

# Find all <li> elements
li_elements = soup.find_all('li', class_='css-5lfssm eu4oa1w0')

# Create a list to store data
data = []

# Extract job details from each <li>
for li in li_elements:
    job_title_span = li.find('h2', class_='jobTitle css-14z7akl eu4oa1w0')
    job_title = job_title_span.text.strip() if job_title_span else "Title not found"

    company_name_span = li.find('span', class_='css-92r8pb')
    company_name = company_name_span.text.strip() if job_title_span else "Company name not found"

    location_span = li.find('div', class_='css-1p0sjhy eu4oa1w0')
    location = location_span.text.strip() if location_span else "Location not found"

    post_date_span = li.find('span', 'date')
    post_date_text = post_date_span.text.strip() if post_date_span else "Post date not found"
    today = datetime.today().strftime("%Y-%m-%d")

    # Check if any of the fields end with "not found"
    if not (job_title.endswith("not found") or company_name.endswith("not found") or location.endswith("not found") or post_date_text.endswith("not found")):
        company_url = get_company_url(company_name)
        data.append({
            'Company Name': company_name,
            'Company URL': company_url if company_url else '',  # Placeholder if URL not found
            'Date of Job Posting': post_date_text,
            'Job Title': job_title,
            'Country': location,
            'Source': 'https://de.indeed.com'
        })

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=['Company Name', 'Company URL', 'Date of Job Posting', 'Job Title', 'Country', 'Source'])

# Save the clean data to an Excel sheet
df.to_excel('job_data.xlsx', index=False)
