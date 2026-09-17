from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import medical_crawler.settings as s
from loguru import logger
from generator.drug_generator import run_generate_drugs
from generator.disease_generator import run_generate_diseases
from generator.guideline_generator import run_generate_guidelines


class HybridFallbackMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super().__init__(settings)
        self.fail_count = {}

    def process_exception(self, request, exception, spider):
        self.fail_count[spider.name] = self.fail_count.get(spider.name, 0) + 1
        if (
            s.CRAWL_MODE in ("hybrid", "mock")
            and self.fail_count[spider.name] >= s.FALLBACK_THRESHOLD
        ):
            logger.warning(f"[HybridFallback] {spider.name}: fail>{s.FALLBACK_THRESHOLD}, switch to GENERATOR mode")
            if spider.name == "cmekg":
                run_generate_diseases()
            elif spider.name == "drug_label":
                run_generate_drugs()
            elif spider.name == "clinical_guideline":
                run_generate_guidelines()
            spider.crawler.engine.close_spider(spider, "fallback_to_generator")
        return super().process_exception(request, exception, spider)


DOWNLOADER_MIDDLEWARES = {
    "medical_crawler.middlewares.HybridFallbackMiddleware": 550,
}
