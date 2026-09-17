import json
import os
import time
from pathlib import Path
import orjson
import redis
from kafka import KafkaProducer
from itemadapter import ItemAdapter
from loguru import logger
from scrapy.exceptions import CloseSpider
import medical_crawler.settings as s
from generator.interaction_generator import ensure_generator_seed


class StatsCollectorPipeline:
    def open_spider(self, spider):
        try:
            self.r = redis.Redis.from_url(s.REDIS_URL, decode_responses=True)
            self.r.ping()
        except Exception as e:
            logger.warning(f"[Stats] Redis unavailable: {e}")
            self.r = None
        self.counter = 0
        self.spider_name = spider.name

    def process_item(self, item, spider):
        self.counter += 1
        if self.r and self.counter % 100 == 0:
            pipe = self.r.pipeline()
            pipe.hincrby(f"crawler:stats:{self.spider_name}", "total_items", 100)
            pipe.hincrby(f"crawler:stats:{self.spider_name}", f"rate_trend:{int(time.time()//60)}", 100)
            pipe.execute()
        if self.counter > s.DAILY_LIMIT:
            raise CloseSpider(f"Reach DAILY_LIMIT={s.DAILY_LIMIT}")
        return item

    def close_spider(self, spider, reason):
        if self.r:
            self.r.hset(f"crawler:stats:{self.spider_name}", mapping={
                "last_finish_ts": int(time.time()),
                "last_reason": reason,
                "total_items": self.counter,
            })


class JsonLinesWriterPipeline:
    def open_spider(self, spider):
        self.fp = open(s.OUTPUT_DIR / f"{spider.name}.jsonl", "a", encoding="utf-8")

    def close_spider(self, spider, reason):
        self.fp.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False)
        self.fp.write(line + "\n")
        return item


class KafkaProducerPipeline:
    def open_spider(self, spider):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=s.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: orjson.dumps(v),
                key_serializer=lambda k: k.encode() if isinstance(k, str) else k,
                retries=3,
            )
            self.producer.send(s.KAFKA_TOPIC, key="ping", value={"type": "hello", "spider": spider.name})
            self.kafka_ok = True
        except Exception as e:
            logger.warning(f"[Kafka] unavailable ({e}), fallback to local JSONL only")
            self.kafka_ok = False

    def close_spider(self, spider, reason):
        if self.kafka_ok:
            self.producer.flush(timeout=10)
            self.producer.close(timeout=10)

    def process_item(self, item, spider):
        if not self.kafka_ok:
            return item
        try:
            msg = {
                "ods_type": spider.name,
                "ts": int(time.time() * 1000),
                "payload": ItemAdapter(item).asdict(),
            }
            self.producer.send(s.KAFKA_TOPIC, key=spider.name, value=msg)
        except Exception as e:
            logger.error(f"[Kafka] send failed: {e}")
        return item
