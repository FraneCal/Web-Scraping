# Start the code with:          scrapy crawl example 
# Storing the data in JSON:     scrapy crawl example -o example.json
# Entering shell:               scrapy shell "example.com"

import scrapy

class ExampleSpider(scrapy.Spider):
    name = 'example'
    start_urls = ['example.com']

    def parse(self, response):
        company_names = response.xpath("//div[@class='logo-container']/img/@alt").getall()

        for company_name in company_names:
            yield{
                "Comapany name": company_name,
            }
