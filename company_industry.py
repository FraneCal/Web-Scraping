import requests


url = 'https://api.thecompaniesapi.com/v1/companies/similar?domains[]=kace.com'
headers = {'Authorization: Basic 3C69nnR1'}


response = requests.get(url, "?token=3C69nnR1")
data = response.json()

print(data)

# main_industry = data[0]['industryMain']
# industries = data[0]['industries']

# print(main_industry)
# print(industries)
