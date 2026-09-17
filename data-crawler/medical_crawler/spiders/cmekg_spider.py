import scrapy
import medical_crawler.settings as s
from medical_crawler.items import DiseaseRawItem
from generator.disease_generator import run_generate_diseases, generate_disease_id


CMEKG_PUBLIC_SAMPLE = [
]


class CmekgSpider(scrapy.Spider):
    name = "cmekg"
    allowed_domains = ["cmekg.cn", "zstellarkg.com"]
    start_urls = ["http://cmekg.cn/"]

    custom_settings = {"CLOSESPIDER_PAGECOUNT": 50}

    def parse(self, response):
        if s.CRAWL_MODE == "mock":
            self.logger.info("CRAWL_MODE=mock, invoke generator directly")
            run_generate_diseases()
            return
        if not CMEKG_PUBLIC_SAMPLE:
            yield DiseaseRawItem(disease_id=None)
            return
        for row in CMEKG_PUBLIC_SAMPLE:
            yield DiseaseRawItem(
                disease_id=generate_disease_id(row.get("name", "")),
                name=row.get("name"),
                icd_code=row.get("icd_code"),
                aliases=row.get("aliases", []),
                department=row.get("department"),
                symptoms=row.get("symptoms", []),
                treatments=row.get("treatments", []),
            )
