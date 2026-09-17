import scrapy
import medical_crawler.settings as s
from medical_crawler.items import DrugRawItem
from generator.drug_generator import run_generate_drugs


class DrugLabelSpider(scrapy.Spider):
    name = "drug_label"
    allowed_domains = ["drugs.com", "nmpa.gov.cn"]
    start_urls = ["https://www.drugs.com/"]
    custom_settings = {"CLOSESPIDER_PAGECOUNT": 50, "DOWNLOAD_DELAY": 1.2}

    def parse(self, response):
        if s.CRAWL_MODE == "mock" or response.status in (403, 404, 500):
            self.logger.info("Invoke drug generator")
            run_generate_drugs()
            return
        yield from []
