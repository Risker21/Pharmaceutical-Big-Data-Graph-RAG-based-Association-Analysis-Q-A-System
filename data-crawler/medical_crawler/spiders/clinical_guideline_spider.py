import scrapy
import medical_crawler.settings as s
from medical_crawler.items import GuidelineRawItem
from generator.guideline_generator import run_generate_guidelines


class ClinicalGuidelineSpider(scrapy.Spider):
    name = "clinical_guideline"
    start_urls = ["https://www.cma.org.cn/"]
    custom_settings = {"CLOSESPIDER_PAGECOUNT": 100}

    def parse(self, response):
        if s.CRAWL_MODE == "mock" or response.status in (403, 404, 500):
            self.logger.info("Invoke guideline generator")
            run_generate_guidelines()
            return
        yield from []
