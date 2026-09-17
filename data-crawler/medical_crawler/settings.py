import os
from pathlib import Path

BOT_NAME = "medical_crawler"
SPIDER_MODULES = ["medical_crawler.spiders"]
NEWSPIDER_MODULE = "medical_crawler.spiders"
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = float(os.getenv("CRAWLER_REQUEST_INTERVAL_MS", "1000")) / 1000.0
RETRY_TIMES = int(os.getenv("CRAWLER_MAX_RETRY", "3"))
CRAWL_MODE = os.getenv("CRAWLER_MODE", "hybrid")
FALLBACK_THRESHOLD = int(os.getenv("CRAWLER_FALLBACK_THRESHOLD", "10"))
DAILY_LIMIT = int(os.getenv("CRAWLER_DAILY_LIMIT", "20000"))

ITEM_PIPELINES = {
    "medical_crawler.pipelines.StatsCollectorPipeline": 100,
    "medical_crawler.pipelines.JsonLinesWriterPipeline": 200,
    "medical_crawler.pipelines.KafkaProducerPipeline": 300,
}

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("CRAWLER_KAFKA_TOPIC", "medical_raw_topic")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/3")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "ods_raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 5
