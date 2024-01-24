from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import random
import time

def get_url(position, location):
    template = "https://de.indeed.com/jobs?q={}&l={}"
    url = template.format(position, location)
    return url

url = get_url('cloud engineer', 'germany')

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


# scroll_increment = 0
# while scroll_increment < 750:
#     driver.execute_script(f"window.scrollTo(0, {scroll_increment * 10});")
#     time.sleep(1)
#     scroll_increment += 75

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)


page_source = driver.page_source
driver.quit()
soup = BeautifulSoup(page_source, "html.parser")

# Find all <li> elements
li_elements = soup.find_all('li', class_='css-5lfssm eu4oa1w0')

# Extract job titles from each <li>
for li in li_elements:
    job_title_span = li.find('h2', class_ = 'jobTitle css-14z7akl eu4oa1w0')
    job_title = job_title_span.text.strip() if job_title_span else "Title not found"

    company_name_span = li.find('span', class_ = 'css-92r8pb')
    company_name = company_name_span.text.strip() if job_title_span else "Company name not found"

    location_span = li.find('div', class_= 'css-1p0sjhy eu4oa1w0')
    location = location_span.text.strip() if location_span else "Location not found"

    print(job_title)
    print(company_name)
    print(location)
