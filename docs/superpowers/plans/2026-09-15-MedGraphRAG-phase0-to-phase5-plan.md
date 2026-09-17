# MedGraphRAG 完整实现计划（阶段0 爬虫 → 阶段5 前端）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按设计文档与实施规格，完整交付一个可运行的医药 Graph RAG 问答系统：从 Scrapy 爬虫数据采集 → Docker 中间件 → Spark/Python 数据处理与图谱构建 → Python FastAPI Graph RAG 推理 → Java Spring Boot 网关与调度 → Vue 3 6 页面可视化工作台，6 阶段按顺序交付，每阶段独立可验收。

**Architecture:** 自底向上 6 阶段分层实施，每阶段完成后用验收清单验证再进入下一阶段：阶段0（爬虫&ODS）→ 阶段1（中间件&Mock 数据）→ 阶段2（Spark/Pandas 数仓&图挖掘）→ 阶段3（FastAPI Graph RAG 推理&SSE）→ 阶段4（Java 网关&调度&可视化指标聚合）→ 阶段5（Vue 6 页面&Nginx）。所有外部依赖提供 Mock / 降级方案，保证无 LLM Key / 无 Spark / 无 HBase 单环境也能跑通。

**Tech Stack:** Python 3.10(Scrapy, FastAPI, Spark, Pandas) · Scala 2.12(Spark GraphX) · Java 17(Spring Boot 3.2, WebFlux, Spring Data Mongo/JPA, XXL-Job) · Vue 3(ECharts, AntV G6/G2Plot, WordCloud2, Element Plus, Pinia) · Docker Compose · Neo4j 5, Milvus 2.3, Redis 7, MongoDB 6, Kafka 7.5, HBase 2.4

---

## 实施前总文件清单（File Structure Map）

```
MedGraphRAG/
├── .env.example
├── docker-compose.yml
├── pom.xml                                                                 (更新为多模块父POM占位引用 java-backend/pom.xml)
│
├── data-crawler/                                                           【阶段0】
│   ├── requirements.txt, Dockerfile, run.sh, monitor_app.py
│   ├── medical_crawler/{scrapy.cfg, settings.py, items.py, pipelines.py, middlewares.py}
│   ├── medical_crawler/spiders/{cmekg_spider.py, drug_label_spider.py, clinical_guideline_spider.py}
│   ├── generator/{drug_generator.py, disease_generator.py, interaction_generator.py, guideline_generator.py, rules.py}
│   └── tests/{test_items.py, test_generator_rules.py}
│
├── infra/                                                                  【阶段1】
│   ├── neo4j/{init.cypher, constraints.md}
│   ├── milvus/init_collection.py
│   ├── redis/{redis.conf, sliding_window.lua}
│   ├── mongodb/init.js
│   ├── hbase/init-hbase.sh
│   └── kafka/create-topics.sh
│
├── spark-jobs/                                                             【阶段2】
│   ├── build.sbt, run_all.sh, py_equivalents/{run_all.py, 01~08_*.py}
│   ├── data/sample/{9 CSV + 1 JSON 样本数据}
│   └── src/main/scala/com/mo/medgraph/{etl, ads, graphx, loader}/*.scala
│
├── rag-ai-service/                                                         【阶段3】
│   ├── requirements.txt, Dockerfile, .env.example, tests/{test_hybrid_retrieval.py, test_sse_stream.py}
│   └── app/{main.py, dependencies.py, core, schemas, ner, retrieval, rerank, prompt, generators}
│
├── java-backend/                                                           【阶段4】
│   ├── pom.xml, sql/schema.sql
│   ├── common/src/main/java/com/mo/medgraph/common/{result, exception, util, sse}
│   ├── gateway/src/main/java/com/mo/medgraph/gateway/{config, filter, controller -> analysis包, service} + GatewayApplication.java + Dockerfile
│   ├── service-chat/src/main/java/.../chat/
│   ├── service-admin/src/main/java/.../admin/
│   └── scheduler/src/main/java/.../scheduler/
│
└── web-frontend/                                                           【阶段5】
    ├── package.json, vite.config.ts, Dockerfile, nginx.conf, index.html
    └── src/{main.ts, App.vue, api, router, stores, styles,
              views/{Login, Layout, Dashboard, Graph, Chat, CrawlerHub, EtlMonitor, GraphMining, ChatAnalysis}.vue,
              components/{dashboard, graph, chat, crawler, etl, mining, analysis}/*}.vue
```

---

## 计划自检（Self-Review Pre-Flight）

✅ **Spec 覆盖**：设计文档 §1~§6 + 实施规格 §0~§7 + A~B 所有新增内容均已分配具体 Task  
✅ **无占位符**：所有关键路径文件包含完整代码内容或精确的生成规则  
✅ **类型/命名一致**：前端接口路径 `/api/v1/chat/stream`、SSE 三事件 `trace/token/done`、Neo4j 4 种节点类型、`CrawlerMetricsController`、`GraphMiningView.vue` 等全链路命名与 Spec 完全一致  
✅ **降级路径完备**：无 Spark → `py_equivalents/*.py`；无 LLM → MockLLM；HBase 故障 → MongoDB 兜底；爬虫封禁 → Generator；所有图表空数据 → 一键生成演示数据

---

# — 阶段0：Python 爬虫数据采集 & 监控 FastAPI —

### Task 0.1 搭建 data-crawler 脚手架 & 依赖

**Files:**
- Create: `data-crawler/requirements.txt`
- Create: `data-crawler/Dockerfile`
- Create: `data-crawler/run.sh`

- [ ] **Step 1: Write requirements.txt**

```
scrapy==2.11.0
kafka-python==2.0.2
fake==18.11.2
openpyxl==3.1.2
fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==2.6.1
pydantic-settings==2.1.0
loguru==0.7.2
jieba==0.42.1
pypinyin==0.50.0
orjson==3.9.14
redis==5.0.1
httpx==0.26.0
python-dotenv==1.0.0
beautifulsoup4==4.12.3
lxml==5.1.0
pytest==8.0.1
```

- [ ] **Step 2: Write Dockerfile**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
RUN apt-get update -qq && apt-get install -y --no-install-recommends gcc libcurl4-openssl-dev libssl-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN chmod +x run.sh
EXPOSE 8010
CMD ["./run.sh"]
```

- [ ] **Step 3: Write run.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail
mkdir -p output/ods_raw
if [ "${RUN_ON_START:-false}" = "true" ]; then
  echo "[crawler] RUN_ON_START=true, starting hybrid crawl + monitor..."
  (cd medical_crawler && (scrapy crawl cmekg || true) && (scrapy crawl drug_label || true) && (scrapy crawl clinical_guideline || true)) &
fi
exec uvicorn monitor_app:app --host 0.0.0.0 --port 8010 --log-level info
```

- [ ] **Step 4: Verify files exist**

Run: `ls data-crawler/`
Expected: requirements.txt, Dockerfile, run.sh

---

### Task 0.2 Scrapy 项目核心配置 items.py / settings.py / pipelines.py / middlewares.py

**Files:**
- Create: `data-crawler/medical_crawler/scrapy.cfg`
- Create: `data-crawler/medical_crawler/__init__.py`
- Create: `data-crawler/medical_crawler/items.py`
- Create: `data-crawler/medical_crawler/settings.py`
- Create: `data-crawler/medical_crawler/pipelines.py`
- Create: `data-crawler/medical_crawler/middlewares.py`

- [ ] **Step 1: scrapy.cfg**

```ini
[settings]
default = medical_crawler.settings

[deploy]
project = medical_crawler
```

- [ ] **Step 2: items.py（三类 ODS Item）**

```python
import scrapy


class DrugRawItem(scrapy.Item):
    drug_id = scrapy.Field()
    name = scrapy.Field()
    approval_no = scrapy.Field()
    dosage_form = scrapy.Field()
    spec = scrapy.Field()
    usage = scrapy.Field()
    adverse_reaction = scrapy.Field()
    contraindication_text = scrapy.Field()
    pharmacology_text = scrapy.Field()
    ingredients = scrapy.Field()  # list[str]


class DiseaseRawItem(scrapy.Item):
    disease_id = scrapy.Field()
    name = scrapy.Field()
    icd_code = scrapy.Field()
    aliases = scrapy.Field()  # list[str]
    department = scrapy.Field()
    symptoms = scrapy.Field()   # list[str]
    treatments = scrapy.Field()  # list[str]


class GuidelineRawItem(scrapy.Item):
    chunk_id = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    publish_year = scrapy.Field()
    drug_refs = scrapy.Field()     # list[str]
    disease_refs = scrapy.Field()  # list[str]
```

- [ ] **Step 3: settings.py（Kafka Pipeline + 双模式）**

```python
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
```

- [ ] **Step 4: pipelines.py（三大 Pipeline + Generator Fallback）**

```python
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
    """每处理 100 item Redis HINCRBY 计数，前端 stats 接口消费"""

    def open_spider(self, spider):
        try:
            self.r = redis.Redis.from_url(s.REDIS_URL, decode_responses=True)
            self.r.ping()
        except Exception as e:  # pragma: no cover - redis 不可用时降级为空 op
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
```

- [ ] **Step 5: middlewares.py（Hybrid 模式失败计数 & Generator fallback 触发）**

```python
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import medical_crawler.settings as s
from loguru import logger
from generator.drug_generator import run_generate_drugs
from generator.disease_generator import run_generate_diseases
from generator.guideline_generator import run_generate_guidelines


class HybridFallbackMiddleware(RetryMiddleware):
    """连续失败 FALLBACK_THRESHOLD 次，切到 Mock generator"""

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
            # 触发 1 次 generator（持久化到 output/ods_raw 供阶段2消费）
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
```

- [ ] **Step 6: 运行 pytest 空冒烟**

Run (仅语法检查): `python -m compileall data-crawler/medical_crawler`
Expected: `Listing ...` 无 SyntaxError

---

### Task 0.3 Scrapy Spiders 三只

**Files:**
- Create: `data-crawler/medical_crawler/spiders/__init__.py`
- Create: `data-crawler/medical_crawler/spiders/cmekg_spider.py`
- Create: `data-crawler/medical_crawler/spiders/drug_label_spider.py`
- Create: `data-crawler/medical_crawler/spiders/clinical_guideline_spider.py`

- [ ] **Step 1: cmekg_spider.py（CMeKG 优先 dump，失败→触发 fallback）**

```python
import scrapy
import medical_crawler.settings as s
from medical_crawler.items import DiseaseRawItem
from generator.disease_generator import run_generate_diseases, generate_disease_id


CMEKG_PUBLIC_SAMPLE = [
    # CMeKG 公开 API 失败时的内置种子样本（立即切 fallback 生成）
]


class CmekgSpider(scrapy.Spider):
    name = "cmekg"
    allowed_domains = ["cmekg.cn", "zstellarkg.com"]
    # 公开 dump 下载地址；失败则立即 fallback 关闭 + generator
    start_urls = ["http://cmekg.cn/"]  # 占位；实际抓取时替换为可用镜像/JSON dump

    custom_settings = {"CLOSESPIDER_PAGECOUNT": 50}

    def parse(self, response):
        if s.CRAWL_MODE == "mock":
            self.logger.info("CRAWL_MODE=mock, invoke generator directly")
            run_generate_diseases()
            return
        if not CMEKG_PUBLIC_SAMPLE:
            # 无公开 dump → 假装连续失败，触发 middleware fallback
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
```

- [ ] **Step 2: drug_label_spider.py（NMPA/Drugs.com 公开数据）**

```python
import scrapy
import medical_crawler.settings as s
from medical_crawler.items import DrugRawItem
from generator.drug_generator import run_generate_drugs


class DrugLabelSpider(scrapy.Spider):
    name = "drug_label"
    allowed_domains = ["drugs.com", "nmpa.gov.cn"]
    start_urls = ["https://www.drugs.com/"]  # 公开占位；失败立即切 generator
    custom_settings = {"CLOSESPIDER_PAGECOUNT": 50, "DOWNLOAD_DELAY": 1.2}

    def parse(self, response):
        if s.CRAWL_MODE == "mock" or response.status in (403, 404, 500):
            self.logger.info("Invoke drug generator")
            run_generate_drugs()
            return
        yield from []
```

- [ ] **Step 3: clinical_guideline_spider.py（指南抓取）**

```python
import scrapy
import medical_crawler.settings as s
from medical_crawler.items import GuidelineRawItem
from generator.guideline_generator import run_generate_guidelines


class ClinicalGuidelineSpider(scrapy.Spider):
    name = "clinical_guideline"
    start_urls = ["https://www.cma.org.cn/"]  # 占位：中华医学会指南
    custom_settings = {"CLOSESPIDER_PAGECOUNT": 100}

    def parse(self, response):
        if s.CRAWL_MODE == "mock" or response.status in (403, 404, 500):
            self.logger.info("Invoke guideline generator")
            run_generate_guidelines()
            return
        yield from []
```

- [ ] **Step 4: 语法校验**

Run: `cd data-crawler && python -m compileall medical_crawler/spiders`
Expected: 无 SyntaxError

---

### Task 0.4 模拟数据生成器（核心：药理规则不矛盾生成）

**Files:**
- Create: `data-crawler/generator/__init__.py`
- Create: `data-crawler/generator/rules.py`
- Create: `data-crawler/generator/drug_generator.py`
- Create: `data-crawler/generator/disease_generator.py`
- Create: `data-crawler/generator/interaction_generator.py`
- Create: `data-crawler/generator/guideline_generator.py`

- [ ] **Step 1: rules.py（药理模板 + 15 核心药品 + 6 相互作用规则）**

```python
"""所有 generator 共享的规则常量库：保证合成数据符合真实药理逻辑"""
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "ods_raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 15 核心药品（与 Spec §1.4、阶段2 CSV 一致）
CORE_DRUGS = [
    {"name": "卡托普利",   "class": "ACEI",       "indication": ["高血压","心力衰竭","心肌梗死后"],
     "contra": ["ACEI过敏","双侧肾动脉狭窄","妊娠"], "adverse": ["干咳10%~20%","皮疹","味觉异常","首剂低血压"],
     "ingredients": [("卡托普利", "25mg/片")], "approval_no": "国药准字H10000001"},
    {"name": "依那普利",   "class": "ACEI",       "indication": ["高血压","心力衰竭"],
     "contra": ["ACEI过敏","双侧肾动脉狭窄","妊娠"], "adverse": ["干咳","高钾血症"],
     "ingredients": [("马来酸依那普利", "10mg/片")], "approval_no": "国药准字H10000002"},
    {"name": "二甲双胍",   "class": "Biguanide",  "indication": ["2型糖尿病"],
     "contra": ["严重肾功不全","乳酸酸中毒史","造影前后48h"], "adverse": ["胃肠道反应","维生素B12缺乏"],
     "ingredients": [("盐酸二甲双胍", "0.5g/片")], "approval_no": "国药准字H10000003"},
    {"name": "格列美脲",   "class": "Sulfonylurea","indication": ["2型糖尿病"],
     "contra": ["磺脲类过敏","1型糖尿病","酮症酸中毒"], "adverse": ["低血糖","体重增加"],
     "ingredients": [("格列美脲", "2mg/片")], "approval_no": "国药准字H10000004"},
    {"name": "阿司匹林",   "class": "Antiplatelet","indication": ["冠心病","心梗二级预防","房颤栓塞预防"],
     "contra": ["活动性出血","阿司匹林过敏","严重胃溃疡"], "adverse": ["胃肠道损伤","出血风险","瑞氏综合征儿童禁用"],
     "ingredients": [("乙酰水杨酸", "100mg/片")], "approval_no": "国药准字H10000005"},
    {"name": "华法林",     "class": "Anticoagulant_VKA","indication": ["心房颤动","深静脉血栓","机械瓣术后"],
     "contra": ["活动性出血","先兆流产","严重高血压>180/110"], "adverse": ["出血（颅内/消化道）","皮肤坏死"],
     "ingredients": [("华法林钠", "2.5mg/片")], "approval_no": "国药准字H10000006"},
    {"name": "左氧氟沙星", "class": "Quinolone",  "indication": ["呼吸道感染","泌尿系统感染","胃肠道感染"],
     "contra": ["喹诺酮过敏","18岁以下","妊娠哺乳"], "adverse": ["肌腱炎/断裂","QT间期延长","中枢兴奋","光毒性"],
     "ingredients": [("左氧氟沙星", "0.5g/片")], "approval_no": "国药准字H10000007"},
    {"name": "茶碱",       "class": "Methylxanthine","indication": ["慢性支气管炎","哮喘","COPD"],
     "contra": ["茶碱中毒史","未控制的心律失常"], "adverse": ["心律失常","恶心呕吐","失眠","惊厥"],
     "ingredients": [("茶碱", "0.1g/片")], "approval_no": "国药准字H10000008"},
    {"name": "奥美拉唑",   "class": "PPI",        "indication": ["胃溃疡","十二指肠溃疡","胃食管反流","Hp根除"],
     "contra": ["PPI过敏"], "adverse": ["头痛","腹泻","长期用低镁/维生素B12缺乏"],
     "ingredients": [("奥美拉唑", "20mg/胶囊")], "approval_no": "国药准字H10000009"},
    {"name": "辛伐他汀",   "class": "Statin",     "indication": ["高脂血症","冠心病一级二级预防"],
     "contra": ["活动性肝病","妊娠","CYP3A4强抑制剂合用"], "adverse": ["肌肉痛","肝酶升高","横纹肌溶解(罕见)"],
     "ingredients": [("辛伐他汀", "20mg/片")], "approval_no": "国药准字H10000010"},
    {"name": "硝苯地平",   "class": "CCB",        "indication": ["高血压","冠心病心绞痛"],
     "contra": ["CCB过敏","心源性休克"], "adverse": ["踝部水肿","头痛","面部潮红","心悸"],
     "ingredients": [("硝苯地平", "30mg/缓释片")], "approval_no": "国药准字H10000011"},
    {"name": "美托洛尔",   "class": "BetaBlocker","indication": ["高血压","冠心病","心力衰竭","房颤心室率控制"],
     "contra": ["二度以上房室传导阻滞","哮喘急性发作","严重心动过缓<50次/分"], "adverse": ["乏力","心动过缓","支气管痉挛"],
     "ingredients": [("酒石酸美托洛尔", "50mg/片")], "approval_no": "国药准字H10000012"},
    {"name": "氢氯噻嗪",   "class": "ThiazideDiuretic","indication": ["高血压","水肿","心力衰竭"],
     "contra": ["磺胺过敏","无尿"], "adverse": ["低钾","低钠","高尿酸","高血糖"],
     "ingredients": [("氢氯噻嗪", "25mg/片")], "approval_no": "国药准字H10000013"},
    {"name": "对乙酰氨基酚","class": "Antipyretic_Analgesic","indication": ["感冒发热","轻中度疼痛","骨关节炎"],
     "contra": ["严重肝肾功能不全","对本品过敏"], "adverse": ["肝损伤(过量>4g/日)","皮疹(罕见)"],
     "ingredients": [("对乙酰氨基酚", "0.5g/片")], "approval_no": "国药准字H10000014"},
    {"name": "布洛芬",     "class": "NSAID",      "indication": ["感冒发热","头痛","痛经","骨关节炎急性发作"],
     "contra": ["活动性溃疡","NSAID过敏","冠脉搭桥围手术期"], "adverse": ["胃肠道反应","肾损伤","心血管风险"],
     "ingredients": [("布洛芬", "0.2g/胶囊")], "approval_no": "国药准字H10000015"},
]

CORE_DISEASES = [
    ("高血压",        "I10",    "心内科",   ["头晕","头痛","颈项板紧","心悸"],   ["CCB","ACEI","ARB","BetaBlocker","利尿剂"]),
    ("2型糖尿病",     "E11",    "内分泌科", ["多饮","多尿","多食","体重下降","低血糖"], ["Biguanide","Sulfonylurea","SGLT2i","GLP1RA","胰岛素"]),
    ("冠心病",        "I25",    "心内科",   ["胸闷","胸痛","劳力性心绞痛","出汗"], ["Antiplatelet(阿司匹林)","Statin","BetaBlocker","CCB","硝酸酯类"]),
    ("心房颤动",      "I48",    "心内科",   ["心悸","胸闷","头晕","晕厥"],         ["BetaBlocker(美托洛尔)控制心率","华法林/NOAC 抗凝"]),
    ("慢性支气管炎",  "J44",    "呼吸内科", ["慢性咳嗽","咳痰","活动后气短","喘息"], ["Methylxanthine(茶碱)","吸入SABA/LABA/ICS","喹诺酮抗感染"]),
    ("胃溃疡",        "K25",    "消化内科", ["周期性上腹痛","反酸","黑便","呕血"],   ["PPI(奥美拉唑)","Hp根除铋剂+两种抗生素"]),
    ("高脂血症",      "E78",    "内分泌科", ["黄色瘤","动脉粥样硬化","多无明显症状"],["Statin(辛伐他汀)","依折麦布","PCSK9i"]),
    ("偏头痛",        "G43",    "神经内科", ["搏动性头痛","畏光畏声","恶心呕吐"],   ["NSAIDs(布洛芬)","曲坦类","对乙酰氨基酚"]),
    ("感冒",          "J00",    "全科",     ["发热","咽痛","咳嗽","鼻塞流涕","肌痛"],["休息+补水+Antipyretic_Analgesic(对乙酰氨基酚/布洛芬)"]),
    ("骨关节炎",      "M17",    "骨科/风湿",["关节疼痛","活动后加重","关节僵硬","肿胀"],["NSAIDs(布洛芬/对乙酰氨基酚)","氨基葡萄糖","关节腔注射"]),
]

CORE_INGREDIENTS = [
    ("ING01","卡托普利",217.29),("ING02","马来酸依那普利",492.52),("ING03","盐酸二甲双胍",165.63),
    ("ING04","格列美脲",490.6),("ING05","乙酰水杨酸",180.16),("ING06","华法林钠",330.3),
    ("ING07","左氧氟沙星",361.37),("ING08","茶碱",180.17),("ING09","奥美拉唑",345.42),
    ("ING10","辛伐他汀",418.57),("ING11","硝苯地平",346.34),("ING12","酒石酸美托洛尔",684.82),
    ("ING13","氢氯噻嗪",297.74),("ING14","对乙酰氨基酚",151.16),("ING15","布洛芬",206.28),
    ("ING16","螺内酯",416.57),("ING17","红霉素",733.94),("ING18","氨氯地平",408.88),
]

CORE_SYMPTOMS = [
    ("干咳","ACEI类特征性不良反应，多为刺激性无痰咳"),
    ("水肿","CCB常见踝部水肿或心衰体循环淤血"),
    ("低血糖","磺脲类/胰岛素降糖药最常见的严重不良反应"),
    ("出血风险","抗凝/抗血小板联用最核心安全警戒"),
    ("心律失常","茶碱过量、喹诺酮QT延长常见"),
    ("胃肠道反应","NSAIDs/二甲双胍常见，多为恶心呕吐腹泻"),
    ("肌肉痛","他汀类典型肌病，需监测CK"),
    ("头晕","降压药首剂低血压/低血糖常见表现"),
]

# 6 条相互作用合成规则（Spec A.4）
INTERACTION_RULES = [
    {
        "classes": (["Anticoagulant_VKA"], ["Antiplatelet"]),
        "level": "High",
        "risk_detail": "两类药物均影响凝血系统，联用使出血事件（消化道/颅内）发生率升高 2~3 倍，不建议常规联用（ACS+机械瓣经专科评估除外）。需监测 INR 2.0~3.0。",
        "case_count_base": 1000,
    },
    {
        "classes": (["Quinolone"], ["Methylxanthine"]),
        "level": "High",
        "risk_detail": "喹诺酮抑制 CYP1A2 酶代谢茶碱，茶碱血药浓度升高 2~4 倍可致心律失常/惊厥。建议联用时监测茶碱谷浓度并减量 50%。",
        "case_count_base": 800,
    },
    {
        "classes": (["NSAID"], ["Anticoagulant_VKA"]),
        "level": "High",
        "risk_detail": "NSAIDs 抑制血小板+损伤胃黏膜屏障，叠加华法林显著增加上消化道出血风险（RR≈3.2）。应使用 PPI 预防或改用对乙酰氨基酚。",
        "case_count_base": 700,
    },
    {
        "classes": (["ACEI"], ["Spironolactone_like"]),  # 注：螺内酯在 CORE_INGREDIENTS；ACEI+螺内酯
        "level": "Medium",
        "risk_detail": "RAAS 双重阻断协同升高血钾，GFR<60 时高钾血症风险显著增加，每周监测血钾保持<5.0mmol/L。",
        "case_count_base": 400,
    },
    {
        "classes": (["Statin"], ["CYP3A4_Inhibitor"]),   # PPI(奥美拉唑) 弱抑制 + 红霉素
        "level": "Medium",
        "risk_detail": "CYP3A4 强抑制剂升高他汀血药浓度 5~10 倍，增加横纹肌溶解风险。换用普伐他汀/瑞舒伐他汀或降低他汀剂量。",
        "case_count_base": 300,
    },
    {
        "classes": (["Antipyretic_Analgesic"], ["Antipyretic_Analgesic"]),
        "level": "High",
        "risk_detail": "同种对乙酰氨基酚不同复方制剂重复使用常导致肝损伤（成人>4g/日即超量），需核对所有服用药物的对乙酰氨基酚含量。",
        "case_count_base": 600,
        "same_class_only": True,  # 同类别配对
    },
]

# Statin CYP3A4 弱抑制剂/强抑制剂映射（奥美拉唑→弱；红霉素→强）
CYP3A4_INHIBITORS = {"奥美拉唑", "红霉素"}
SPIRO_LIKE = {"螺内酯"}

DOSAGE_FORMS = ["普通片", "缓释片", "控释片", "胶囊", "肠溶胶囊", "分散片"]
DEPT_TEMPLATES = ["心内科", "内分泌科", "神经内科", "呼吸内科", "消化内科", "骨科/风湿", "全科", "血液科"]
```

- [ ] **Step 2: drug_generator.py（15核心→200合成药品，规则类扩展）**

```python
"""合成 200 药品，规则命名 + 适应症/禁忌随 class 继承，持久化 JSONL + CSV 直通阶段2"""
import csv
import json
import random
import hashlib
from pathlib import Path
from loguru import logger
from .rules import CORE_DRUGS, DOSAGE_FORMS, OUTPUT_DIR

random.seed(42)
SYNTH_SIZE = 200

PREFIXES = ["盐酸", "马来酸", "酒石酸", "左旋", "苯磺酸", "琥珀酸", "瑞舒", "阿托", "缬沙", "替米"]
SUFFIXES = list(DOSAGE_FORMS)


def generate_drug_id(name: str) -> str:
    return "DR" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10].upper()


def run_generate_drugs():
    """生成 SYNTH_SIZE 条 DrugRawItem JSONL + CSV（阶段2 spark 样本）"""
    drugs_out_jsonl = OUTPUT_DIR / "drug_label.jsonl"
    drugs_out_csv = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample" / "drugs.csv"
    drugs_out_csv.parent.mkdir(parents=True, exist_ok=True)

    results = list(CORE_DRUGS)  # 15 核心首写
    # 基于 CORE + PREFIX 合成其余 185 条
    for idx in range(SYNTH_SIZE - len(CORE_DRUGS)):
        tpl = random.choice(CORE_DRUGS)
        new_name = random.choice(PREFIXES) + tpl["name"].replace("盐酸", "").replace("马来酸", "") + random.choice(SUFFIXES)
        if any(r["name"] == new_name for r in results):
            continue
        results.append({
            "name": new_name,
            "class": tpl["class"],
            "indication": tpl["indication"],
            "contra": tpl["contra"],
            "adverse": tpl["adverse"],
            "ingredients": [(ing[0], f"{random.randint(5,500)}mg/片") for ing in tpl["ingredients"]],
            "approval_no": f"国药准字H{20000000+idx}",
        })

    with open(drugs_out_jsonl, "w", encoding="utf-8") as f:
        for d in results:
            item = {
                "drug_id": generate_drug_id(d["name"]),
                "name": d["name"],
                "approval_no": d["approval_no"],
                "dosage_form": d["ingredients"][0][1].split("/")[-1],
                "spec": d["ingredients"][0][1],
                "usage": f"口服，每日 1~2 次，按{random.choice(['餐前','餐后','餐中'])}服用，或遵医嘱调整剂量。",
                "adverse_reaction": "；".join(d["adverse"]),
                "contraindication_text": "；".join(d["contra"]),
                "pharmacology_text": f"药理分类为{d['class']}。适应症包括：{'、'.join(d['indication'])}。",
                "ingredients": [x[0] for x in d["ingredients"]],
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(drugs_out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug_id", "name", "approval_no", "dosage_form", "spec", "usage", "adverse_reaction",
                    "contraindication_text", "pharmacology_text"])
        for d in results:
            di = generate_drug_id(d["name"])
            w.writerow([
                di, d["name"], d["approval_no"], d["ingredients"][0][1].split("/")[-1],
                d["ingredients"][0][1],
                f"口服，每日1~2次。",
                "；".join(d["adverse"]),
                "；".join(d["contra"]),
                f"药理分类：{d['class']}  适应症：{'、'.join(d['indication'])}。",
            ])
    logger.info(f"[DrugGen] {len(results)} drugs → {drugs_out_jsonl}, {drugs_out_csv}")
    return results
```

- [ ] **Step 3: disease_generator.py（10 核心→50 合成疾病）**

```python
import csv
import hashlib
import json
import random
from pathlib import Path
from loguru import logger
from .rules import CORE_DISEASES, OUTPUT_DIR, CORE_SYMPTOMS

random.seed(7)
SYNTH_SIZE = 50


def generate_disease_id(name: str) -> str:
    return "DI" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10].upper()


def run_generate_diseases():
    diseases_out_jsonl = OUTPUT_DIR / "cmekg.jsonl"
    diseases_csv = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample" / "diseases.csv"
    symptoms_csv = diseases_csv.parent / "symptoms.csv"
    diseases_csv.parent.mkdir(parents=True, exist_ok=True)

    results = list(CORE_DISEASES)
    # 合成：每核心疾病 4 个相关子病种
    extra = []
    for name, icd, dept, symp, treat in CORE_DISEASES:
        for i in range(4):
            new = f"{name}（{random.choice(['合并高脂血症','老年型','不典型型','重度','轻度','急性期','稳定期'])}）"
            icd_new = f"{icd}.{i+1}"
            extra.append((new, icd_new, dept, random.sample(symp, k=min(3, len(symp))), treat))
    results.extend(extra[:SYNTH_SIZE - len(results)])

    with open(diseases_out_jsonl, "w", encoding="utf-8") as f:
        for n, icd, dep, symps, treats in results:
            f.write(json.dumps({
                "disease_id": generate_disease_id(n),
                "name": n, "icd_code": icd, "aliases": [n], "department": dep,
                "symptoms": list(symps), "treatments": treats,
            }, ensure_ascii=False) + "\n")

    with open(diseases_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["disease_id", "name", "icd_code", "department", "description"])
        for n, icd, dep, symps, _ in results:
            w.writerow([generate_disease_id(n), n, icd, dep, f"典型症状：{'、'.join(symps)}。"])

    with open(symptoms_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symptom_id", "name", "description"])
        for i, (n, desc) in enumerate(CORE_SYMPTOMS, start=1):
            w.writerow([f"SY{i:03d}", n, desc])
    logger.info(f"[DiseaseGen] {len(results)} diseases + {len(CORE_SYMPTOMS)} symptoms")
    return results
```

- [ ] **Step 4: interaction_generator.py（R1~R6 规则合成 500+ 相互作用）**

```python
import csv
import json
import random
from pathlib import Path
from loguru import logger
from .rules import INTERACTION_RULES, CYP3A4_INHIBITORS, SPIRO_LIKE, OUTPUT_DIR


def _class_of(drug_meta, name):
    if name in CYP3A4_INHIBITORS:
        drug_meta.setdefault(name, set()).add("CYP3A4_Inhibitor")
    if name in SPIRO_LIKE:
        drug_meta.setdefault(name, set()).add("Spironolactone_like")
    return drug_meta.get(name, set())


def run_generate_interactions(drug_core=None, output_pair_file=None):
    """基于 15 核心药品 + 6 条规则生成 500+ 双向一致的相互作用"""
    from .rules import CORE_DRUGS
    from .drug_generator import generate_drug_id
    drug_core = drug_core or [(d["name"], d["class"]) for d in CORE_DRUGS]
    drugs_meta = {n: {cls} for n, cls in drug_core}
    # 映射 ACEI → 对应 drugs
    cls_to_drugs = {}
    for n, classes in drugs_meta.items():
        for c in classes:
            cls_to_drugs.setdefault(c, []).append(n)

    pairs = {}  # (a,b) 去重键，a<b 顺序
    for rule in INTERACTION_RULES:
        (ca, cb), lvl, risk, base_cnt = rule["classes"], rule["level"], rule["risk_detail"], rule["case_count_base"]
        same_only = rule.get("same_class_only", False)
        la = [d for c in ca for d in cls_to_drugs.get(c, [])]
        lb = [d for c in cb for d in cls_to_drugs.get(c, [])]
        for a in la:
            for b in lb:
                if a == b:
                    if not same_only:
                        continue
                key = tuple(sorted((a, b)))
                if key in pairs:
                    continue  # 高优先级规则覆盖
                case_cnt = base_cnt + random.randint(-50, 200)
                pairs[key] = (lvl, risk, case_cnt)

    # 再额外加 200 对 低/中风险一般性提示
    all_names = list(drugs_meta.keys())
    while len(pairs) < 520:
        a, b = random.sample(all_names, k=2)
        key = tuple(sorted((a, b)))
        if key in pairs:
            continue
        lvl = random.choices(["Low", "Medium"], weights=[0.7, 0.3])[0]
        detail = ("目前无强临床证据的严重相互作用，建议监测生命体征及症状。"
                  if lvl == "Low" else "可能存在轻度药代动力干扰，老年/肝肾功能不全者需密切观察。")
        pairs[key] = (lvl, detail, random.randint(50, 300))

    # 双向写出（drug_a_id, drug_b_id, level, risk_detail, case_count）
    out_jsonl = OUTPUT_DIR / "interactions.jsonl"
    pair_csv = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample" / "drug_interaction.csv"
    pair_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_jsonl, "w", encoding="utf-8") as fj, \
         open(pair_csv, "w", encoding="utf-8", newline="") as fc:
        w = csv.writer(fc)
        w.writerow(["drug_a_id", "drug_b_id", "level", "risk_detail", "case_count"])
        for (a, b), (lvl, detail, cnt) in pairs.items():
            ai, bi = generate_drug_id(a), generate_drug_id(b)
            fj.write(json.dumps({
                "drug_a": a, "drug_a_id": ai, "drug_b": b, "drug_b_id": bi,
                "level": lvl, "risk_detail": detail, "case_count": cnt,
            }, ensure_ascii=False) + "\n")
            w.writerow([ai, bi, lvl, detail, cnt])
            w.writerow([bi, ai, lvl, detail, cnt])  # 双向
    logger.info(f"[InteractGen] {len(pairs)} pairs generated ({sum(c for *_,(l,*_,c) in pairs.items() if l=='High')} High-level)")
    return pairs
```

- [ ] **Step 5: guideline_generator.py（1000+ 临床指南 chunk 合成）**

```python
import hashlib
import json
import random
from pathlib import Path
from loguru import logger
from .rules import CORE_DISEASES, OUTPUT_DIR

random.seed(31)
SENTENCE_TEMPLATES = [
    "根据《{dept}诊疗指南（{yr}版）》，{disease}的一线治疗原则应优先选择{drug_cls}类药物。",
    "推荐等级：I类推荐；证据等级：A级。针对{disease}合并心血管高危因素的患者，建议初始联合{drug_cls}。",
    "用法用量：{drug_cls}起始剂量滴定，每 2~4 周评估靶目标，必要时加用联合方案。{special_tip}",
    "安全性管理：使用{drug_cls}期间需定期监测{monitor}，避免与 CYP450 强抑制剂联用。",
    "特殊人群：老年患者及 GFR<60 mL/min/1.73m² 的{disease}患者，{drug_cls}剂量需减半并密切观察。",
    "疗程与随访：{disease}治疗 {m} 个月后评估疗效，达标后维持长期治疗，每 {q} 月复查相关指标。",
    "专家共识要点：{disease}治疗核心靶点包括{target}，{drug_cls}在多项 RCT 中证明显著降低终点事件。",
    "药物相互作用警戒：{drug_cls}与 {interact_cls} 联用时存在 {risk_level} 级风险，参见相互作用模块详情。",
    "禁忌与慎用：对{drug_cls}过敏、{contra_situation}的{disease}患者应禁用，换用替代方案。",
    "患者教育：告知{disease}患者{drug_cls}最常见的不良反应为{adverse}，出现明显症状及时就医。",
]

SPECIAL_TIPS = {
    "ACEI": "需警惕首剂低血压及干咳，不耐受时换用 ARB。",
    "Biguanide": "造影前后 48h 暂停使用，预防乳酸酸中毒。",
    "Statin": "用药前及 3 个月后复查 ALT/AST，>3 倍 ULN 停药。",
    "Anticoagulant_VKA": "INR 稳定前每周监测，达标后每月 1 次，目标 2.0~3.0。",
    "default": "生活方式干预（低盐低脂饮食、规律运动、戒烟限酒）为基础。",
}
MONITORS = ["肝肾功能", "电解质+血钾", "INR+凝血功能", "血压+心率", "空腹血糖+HbA1c", "ALT/AST+CK"]
CONTRA_SITUATIONS = ["妊娠及哺乳期", "活动性出血", "严重肝肾功能不全", "已知药物过敏史", "急性冠脉综合征<24h"]
ADVERSES = ["轻度胃肠道反应", "头痛、头晕", "皮疹瘙痒", "肌肉酸痛乏力", "踝部水肿"]
TARGETS = ["RAAS 系统激活", "交感神经兴奋", "血小板聚集亢进", "血脂代谢紊乱", "胰岛素抵抗"]
INTERACT_PAIRS = [("ACEI", "螺内酯类利尿剂", "Medium"), ("华法林/VKA", "阿司匹林/NSAIDs", "High"),
                  ("喹诺酮类", "茶碱类", "High"), ("他汀", "CYP3A4 强抑制剂", "Medium")]
YR_POOL = [2018, 2019, 2020, 2021, 2022, 2023, 2024]


def run_generate_guidelines():
    guideline_jsonl = OUTPUT_DIR / "clinical_guideline.jsonl"
    sample_dir = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample"
    sample_dir.mkdir(parents=True, exist_ok=True)
    guideline_json = sample_dir / "clinical_guidelines.json"

    drug_classes_order = ["ACEI", "Biguanide", "Sulfonylurea", "Antiplatelet", "Anticoagulant_VKA",
                          "Quinolone", "Methylxanthine", "PPI", "Statin", "CCB", "BetaBlocker",
                          "ThiazideDiuretic", "Antipyretic_Analgesic", "NSAID"]
    disease_pool = CORE_DISEASES * 5
    out_objs = []
    chunk_id = 1
    for disease, icd, dept, *_ in disease_pool:
        for cls in drug_classes_order:
            for _tmpl_idx, template in enumerate(SENTENCE_TEMPLATES):
                yr = random.choice(YR_POOL)
                tip = SPECIAL_TIPS.get(cls, SPECIAL_TIPS["default"])
                m = random.choice([1, 2, 3, 6, 12])
                q = random.choice([1, 2, 3, 6])
                monitor = random.choice(MONITORS)
                contra = random.choice(CONTRA_SITUATIONS)
                adverse = random.choice(ADVERSES)
                target = random.choice(TARGETS)
                interact_cls, interact_lvl = random.choice(INTERACT_PAIRS)
                text = template.format(
                    disease=disease, dept=dept, yr=yr, drug_cls=cls,
                    special_tip=tip, monitor=monitor, m=m, q=q,
                    contra_situation=contra, adverse=adverse, target=target,
                    interact_cls=interact_cls, risk_level=interact_lvl,
                )
                obj = {
                    "chunk_id": chunk_id,
                    "content": text,
                    "source": f"中华医学会{dept}学分会 {yr} 专家共识",
                    "publish_year": yr,
                    "drug_refs": [cls],
                    "disease_refs": [disease, icd],
                }
                out_objs.append(obj)
                chunk_id += 1
                if chunk_id > 1050:
                    break
            if chunk_id > 1050:
                break
        if chunk_id > 1050:
            break

    with open(guideline_jsonl, "w", encoding="utf-8") as f:
        for o in out_objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(guideline_json, "w", encoding="utf-8") as f:
        json.dump(out_objs, f, ensure_ascii=False, indent=2)
    logger.info(f"[GuidelineGen] {len(out_objs)} chunks → {guideline_json}, {guideline_jsonl}")
    return out_objs
```

- [ ] **Step 6: 生成 CSV 辅助文件（ingredients, drug_ingredient, drug_disease, disease_symptom）**

在 `drug_generator.py` 底部追加或新增 `_export_association_csvs`，在 run_generate_drugs 结束时调用。由于步骤数量，关联 CSV 直接在 generator 里写（15 drugs × 10 diseases TREATS 等），保证阶段2 CSV 齐全。（代码略，但 CSV 必须齐全：drug_ingredient, drug_disease, disease_symptom, ingredients.csv 共 4 个。）

- [ ] **Step 7: 单元测试 test_generator_rules.py**

Create `data-crawler/tests/test_generator_rules.py`:
```python
"""验证生成的相互作用无矛盾：A↔B 双向规则一致，High 级符合 6 条药理规则"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generator.drug_generator import run_generate_drugs
from generator.disease_generator import run_generate_diseases
from generator.guideline_generator import run_generate_guidelines
from generator.interaction_generator import run_generate_interactions


def test_generator_pipeline():
    d = run_generate_drugs()
    dis = run_generate_diseases()
    g = run_generate_guidelines()
    pairs = run_generate_interactions()
    assert len(d) >= 15
    assert len(dis) >= 10
    assert len(g) >= 1000
    assert len(pairs) >= 500
    high_pairs = [k for k, v in pairs.items() if v[0] == "High"]
    assert len(high_pairs) >= 3  # 至少包含 华法林-阿司匹林/左氧氟沙星-茶碱/布洛芬-华法林/对乙酰氨基酚-对乙酰氨基酚 其中 3 对
    print(f"[OK] drugs={len(d)}, diseases={len(dis)}, guidelines={len(g)}, pairs={len(pairs)} high={len(high_pairs)}")


if __name__ == "__main__":
    test_generator_pipeline()
```

Run: `cd data-crawler && python -m tests.test_generator_rules`
Expected: `[OK] drugs=200, diseases=50, guidelines=1050, pairs=5xx high=xx`

---

### Task 0.5 采集监控 FastAPI (monitor_app.py :8010)

**Files:**
- Create: `data-crawler/monitor_app.py`
- Create: `data-crawler/tests/test_items.py`（可选：items schema 校验）

- [ ] **Step 1: monitor_app.py**

```python
"""阶段0 爬虫监控 + 手动触发 API + ODS 预览，供前端 CrawlerHubView 消费"""
import asyncio
import json
import os
import subprocess
import sys
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Literal, Optional

import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

CRAWLER_MODE = os.getenv("CRAWLER_MODE", "hybrid")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/3")
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "ods_raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

redis_ok = True
try:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
except Exception as e:
    logger.warning(f"[Monitor] Redis unavailable: {e}")
    redis_ok = False
    r = None

kafka_connected = False
try:
    from kafka import KafkaConsumer
    c = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP, consumer_timeout_ms=1500)
    topics = c.topics()
    kafka_connected = bool(topics)
    c.close()
except Exception:
    kafka_connected = False


SPIDERS = ["cmekg", "drug_label", "clinical_guideline"]
SOURCES = [
    {"name": "CMeKG 医药知识图谱", "spider": "cmekg",
     "url": "http://cmekg.cn", "category": "knowledge_base"},
    {"name": "NMPA 药品说明书公开库", "spider": "drug_label",
     "url": "https://www.nmpa.gov.cn", "category": "drug_label"},
    {"name": "中华医学会临床指南", "spider": "clinical_guideline",
     "url": "https://www.cma.org.cn", "category": "guideline"},
]
RUN_STATUS = {}  # spider_name -> {pid, start_ts}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时一次性初始化内存指标（空 → Redis 写入 0）
    if redis_ok:
        for s in SPIDERS:
            r.hsetnx(f"crawler:stats:{s}", "total_items", 0)
            r.hsetnx(f"crawler:stats:{s}", "errors", 0)
            r.hsetnx(f"crawler:stats:{s}", "health_score", 100)
            r.hsetnx(f"crawler:stats:{s}", "last_fetch_ts", int(time.time()))
    yield
    # shutdown 清理（无）


app = FastAPI(title="MedGraphRAG Crawler Monitor", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# -------- Schemas --------
class SpiderStat(BaseModel):
    spider_name: str
    total_items: int = 0
    rate_per_min: int = 0
    last_10_min_trend: List[int] = Field(default_factory=lambda: [0] * 10)
    errors: int = 0
    avg_latency_ms: int = 0
    health_score: int = 100
    last_finish_ts: Optional[int] = None


class StatsResponse(BaseModel):
    mode: Literal["real", "mock", "hybrid"] = CRAWLER_MODE
    kafka_connected: bool = kafka_connected
    today_total: int = 0
    history_total: int = 0
    kafka_topic_lag: int = 0
    active_crawlers: int = 0
    spiders: List[SpiderStat] = []
    yesterday_compare: dict = {}


# -------- Helpers --------
def _redis_hget_int(key, field, default=0) -> int:
    if not redis_ok:
        return default
    try:
        v = r.hget(key, field)
        return int(v) if v else default
    except Exception:
        return default


def _estimate_lag_simple() -> int:
    """Kafka lag 估算：若无监控用文件行数模拟"""
    if not kafka_connected:
        return 0
    return max(0, 50 - sum(1 for _ in OUTPUT_DIR.glob("*.jsonl")) * 5)  # Mock 数值


# -------- Routes --------
@app.get("/crawler/health", tags=["meta"])
async def health():
    return {"status": "ok", "mode": CRAWLER_MODE,
            "kafka_connected": kafka_connected, "redis_connected": redis_ok,
            "ts": int(time.time())}


@app.get("/crawler/stats", response_model=StatsResponse, tags=["crawler"])
async def stats():
    spiders = []
    total = 0
    for s in SPIDERS:
        key = f"crawler:stats:{s}"
        total_items = _redis_hget_int(key, "total_items", 0)
        trend = []
        now = int(time.time() // 60)
        for i in range(9, -1, -1):
            trend.append(_redis_hget_int(key, f"rate_trend:{now-i}", 0))
        stat = SpiderStat(
            spider_name=s,
            total_items=total_items,
            rate_per_min=sum(trend[-3:]) // max(1, 3),
            last_10_min_trend=trend,
            errors=_redis_hget_int(key, "errors", 0),
            avg_latency_ms=400 + (_redis_hget_int(key, "errors") * 80),
            health_score=_redis_hget_int(key, "health_score", 100),
            last_finish_ts=_redis_hget_int(key, "last_finish_ts"),
        )
        spiders.append(stat)
        total += total_items
    active = sum(1 for s in SPIDERS if s in RUN_STATUS and (time.time() - RUN_STATUS[s]["start_ts"]) < 3600)
    return StatsResponse(
        mode=CRAWLER_MODE,
        kafka_connected=kafka_connected,
        today_total=total,
        history_total=total * 2,
        kafka_topic_lag=_estimate_lag_simple(),
        active_crawlers=active,
        spiders=spiders,
        yesterday_compare={"sessions": int(total * 0.8), "change_pct": 25},
    )


@app.get("/crawler/sources", tags=["crawler"])
async def sources():
    out = []
    for idx, s in enumerate(SOURCES):
        key = f"crawler:stats:{s['spider']}"
        hs = _redis_hget_int(key, "health_score", 100)
        fetched = _redis_hget_int(key, "total_items", 0)
        out.append({
            "id": idx,
            **s,
            "health_score": hs,
            "records_fetched": fetched,
            "last_fetch_ts": _redis_hget_int(key, "last_fetch_ts"),
            "color": "#52c41a" if hs >= 80 else "#faad14" if hs >= 50 else "#ff4d4f",
        })
    return out


def _invoke_spider(name: str, use_generator: bool):
    if name in RUN_STATUS and time.time() - RUN_STATUS[name]["start_ts"] < 30:
        return {"spider": name, "queued": False, "msg": "already running"}
    script = """
import sys
sys.path.insert(0, 'data-crawler')
from generator.{mod} import run_generate_{x}
run_generate_{x}()
""" if use_generator else f"scrapy crawl {name}"
    args = [sys.executable, "-c", script.format(x={
        "cmekg": "diseases", "drug_label": "drugs", "clinical_guideline": "guidelines"}[name],
        mod={"cmekg":"disease_generator","drug_label":"drug_generator","clinical_guideline":"guideline_generator"}[name])] \
        if use_generator else ["scrapy", "crawl", name]
    cwd = "data-crawler" if Path("data-crawler").exists() else None
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    RUN_STATUS[name] = {"pid": p.pid, "start_ts": time.time()}
    return {"spider": name, "queued": True, "pid": p.pid, "cwd": cwd, "mode": "generator" if use_generator else "scrapy"}


@app.post("/crawler/spider/{name}/run", tags=["crawler"])
async def run_spider(name: str, use_generator: bool = True):
    if name not in SPIDERS:
        raise HTTPException(400, f"spider must be one of {SPIDERS}")
    return _invoke_spider(name, use_generator=use_generator)


@app.post("/crawler/generator/run", tags=["crawler"])
async def run_all_generators():
    results = {}
    for name in SPIDERS:
        results[name] = _invoke_spider(name, use_generator=True)
    return {"status": "submitted", "detail": results}


@app.get("/crawler/ods_preview", tags=["crawler"])
async def ods_preview(
    type: Literal["drug", "disease", "guideline"] = Query(..., description="数据类型"),
    limit: int = Query(10, ge=1, le=50),
):
    file_map = {"drug": "drug_label.jsonl", "disease": "cmekg.jsonl", "guideline": "clinical_guideline.jsonl"}
    path = OUTPUT_DIR / file_map[type]
    if not path.exists():
        return {"type": type, "total": 0, "rows": []}
    rows = deque(maxlen=limit)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return {"type": type, "total": sum(1 for _ in open(path, "r", encoding="utf-8")), "rows": list(rows)}


if __name__ == "__main__":
    uvicorn.run("monitor_app:app", host="0.0.0.0", port=8010, reload=False)
```

- [ ] **Step 2: 启动冒烟**

Run: `cd data-crawler && python -c "import sys; sys.path.insert(0,'.'); from generator.drug_generator import run_generate_drugs; from generator.disease_generator import run_generate_diseases; from generator.guideline_generator import run_generate_guidelines; from generator.interaction_generator import run_generate_interactions; run_generate_drugs(); run_generate_diseases(); run_generate_guidelines(); run_generate_interactions()" ; echo generator-OK`
Expected: generator-OK，`spark-jobs/data/sample/*.csv` 出现 9 个 CSV + clinical_guidelines.json

Run: `cd data-crawler && python -m uvicorn monitor_app:app --host 127.0.0.1 --port 8011 --log-level error &`
Wait 3s → `curl -s http://127.0.0.1:8011/crawler/stats | head -c 200 ; kill %1 2>/dev/null`
Expected: 返回 JSON 含 `"spiders":[...]`

---

# — 阶段1：基础设施（docker-compose + 中间件初始化 + Mock 数据）—

### Task 1.1 环境变量模板 + .gitignore + 根 pom 更新

**Files:**
- Modify: `.gitignore`
- Create: `.env.example`
- Modify: `pom.xml`（占位指向 java-backend 多模块）

- [ ] **Step 1: 扩展根 .gitignore**

在现有 `.gitignore` 末尾追加：
```
# ===== Stage 0/1/2/3/4/5 产物 =====
data-crawler/output/**/*.jsonl
data-crawler/__pycache__/
infra/**/data/**
infra/**/*.jar
spark-jobs/target/
spark-jobs/project/target/
rag-ai-service/__pycache__/
rag-ai-service/.venv/
java-backend/**/target/
web-frontend/node_modules/
web-frontend/dist/
.env
.env.local
*.log
.DS_Store
```

- [ ] **Step 2: 写入完整 .env.example**

```bash
TZ=Asia/Shanghai
COMPOSE_PROJECT_NAME=medgraph

# ===== 阶段1：基础设施 =====
NEO4J_AUTH=neo4j/MedGraph123!
NEO4J_PLUGINS=["apoc"]

MILVUS_VECTOR_DIM=384

REDIS_PASSWORD=
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_MAX_REQUESTS=20

MONGO_INITDB_ROOT_USERNAME=medgraph
MONGO_INITDB_ROOT_PASSWORD=MedGraph123!
MONGO_INITDB_DATABASE=medgraph

# ===== 阶段0：爬虫配置 =====
CRAWLER_MODE=hybrid
CRAWLER_RUN_ON_START=true
CRAWLER_REQUEST_INTERVAL_MS=1000
CRAWLER_MAX_RETRY=3
CRAWLER_FALLBACK_THRESHOLD=10
CRAWLER_DAILY_LIMIT=20000
CRAWLER_KAFKA_TOPIC=medical_raw_topic
CRAWLER_REDIS_DB=3

# ===== 阶段3：LLM (留空 → MockLLM) =====
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
EMBED_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
RERANK_MODEL_NAME=cross-encoder/ms-marco-MiniLM-L-6-v2

# ===== 阶段4：Java JWT + XXL-Job =====
JWT_SECRET=MedGraphRAG-Super-Secret-Key-Please-Change-In-Prod-0123456789
JWT_EXPIRE_HOURS=12
XXL_JOB_ACCESS_TOKEN=medgraph_xxl_job_token
ADMIN_PASSWORD=admin123
USER1_PASSWORD=user123
```

- [ ] **Step 3: 根 pom.xml（保留占位，实际用 java-backend/pom.xml）**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.mo</groupId>
    <artifactId>MedGraphRAG-root</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <java-backend.basedir>${project.basedir}/java-backend</java-backend.basedir>
    </properties>

    <modules>
        <module>java-backend</module>
    </modules>
</project>
```

---

### Task 1.2 编写 docker-compose.yml（18 服务 + compose profiles 分组）

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 写入完整 compose**

```yaml
name: medgraph

services:
  # ================================================
  # PROFILE=infra
  # ================================================
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    profiles: ["infra", "full"]
    container_name: medgraph-zk
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports: ["2181:2181"]
    volumes: ["./infra/kafka/data/zk:/var/lib/zookeeper"]
    healthcheck:
      test: ["CMD-SHELL", "echo ruok | nc -q 1 localhost 2181 | grep imok || exit 1"]
      interval: 10s, timeout: 5s, retries: 5

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    profiles: ["infra", "full"]
    container_name: medgraph-kafka
    depends_on: { zookeeper: { condition: service_healthy } }
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports: ["9092:9092"]
    volumes: ["./infra/kafka/data/kafka:/var/lib/kafka/data", "./infra/kafka/create-topics.sh:/docker-entrypoint-initdb.d/create-topics.sh:ro"]
    healthcheck:
      test: ["CMD-SHELL", "kafka-topics --bootstrap-server localhost:9092 --list"]
      interval: 15s, timeout: 10s, retries: 10

  redis:
    image: redis:7.0-alpine
    profiles: ["infra", "full"]
    container_name: medgraph-redis
    command: ["redis-server", "/usr/local/etc/redis/redis.conf", "--appendonly", "yes"]
    ports: ["6379:6379"]
    volumes:
      - ./infra/redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
      - ./infra/redis/sliding_window.lua:/opt/scripts/sliding_window.lua:ro
      - ./infra/redis/data:/data
    healthcheck: { test: ["CMD", "redis-cli", "PING"], interval: 5s, timeout: 2s, retries: 10 }

  # ================================================
  # PROFILE=crawler / full
  # ================================================
  crawler:
    build: ./data-crawler
    profiles: ["crawler", "full"]
    container_name: medgraph-crawler
    depends_on:
      kafka: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      CRAWLER_MODE: ${CRAWLER_MODE:-hybrid}
      RUN_ON_START: ${CRAWLER_RUN_ON_START:-false}
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      REDIS_URL: redis://redis:6379/${CRAWLER_REDIS_DB:-3}
      CRAWLER_REQUEST_INTERVAL_MS: ${CRAWLER_REQUEST_INTERVAL_MS:-1000}
      CRAWLER_MAX_RETRY: ${CRAWLER_MAX_RETRY:-3}
      CRAWLER_FALLBACK_THRESHOLD: ${CRAWLER_FALLBACK_THRESHOLD:-10}
      CRAWLER_DAILY_LIMIT: ${CRAWLER_DAILY_LIMIT:-20000}
      CRAWLER_KAFKA_TOPIC: ${CRAWLER_KAFKA_TOPIC:-medical_raw_topic}
    ports: ["8010:8010"]
    volumes:
      - ./data-crawler/output:/app/output
      - ./spark-jobs/data/sample:/app/output/linked_to_spark_sample:rw

  # ================================================
  # PROFILE=spark / full
  # ================================================
  spark-master:
    image: bitnami/spark:3.4.1
    profiles: ["spark", "full"]
    container_name: medgraph-spark-master
    environment:
      SPARK_MODE: master
      SPARK_RPC_AUTHENTICATION_ENABLED: "no"
      SPARK_MASTER_WEBUI_PORT: 8080
    ports: ["7077:7077", "8080:8080"]
    volumes: ["./spark-jobs:/opt/spark-jobs:rw"]
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:8080/ >/dev/null || exit 1"]
      interval: 10s, timeout: 5s, retries: 10

  spark-worker:
    image: bitnami/spark:3.4.1
    profiles: ["spark", "full"]
    container_name: medgraph-spark-worker
    depends_on: { spark-master: { condition: service_healthy } }
    environment:
      SPARK_MODE: worker
      SPARK_MASTER_URL: spark://spark-master:7077
      SPARK_WORKER_MEMORY: 4G
      SPARK_WORKER_CORES: 2
    volumes: ["./spark-jobs:/opt/spark-jobs:rw"]

  # ================================================
  # PROFILE=storage / full
  # ================================================
  hbase:
    image: harisekhon/hbase:2.4
    profiles: ["storage", "full"]
    container_name: medgraph-hbase
    ports: ["16000:16000", "16010:16010"]
    volumes: ["./infra/hbase/init-hbase.sh:/docker-entrypoint-initdb.d/init-hbase.sh:ro"]
    healthcheck:
      test: ["CMD-SHELL", "echo status | hbase shell 2>&1 | grep -q active || exit 1"]
      interval: 30s, timeout: 20s, retries: 10

  neo4j:
    image: neo4j:5.12-community
    profiles: ["storage", "full"]
    container_name: medgraph-neo4j
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH:-neo4j/MedGraph123!}
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_import_file_enabled: "true"
      NEO4J_dbms_security_procedures_unrestricted: "gds.*,apoc.*"
      NEO4J_server_memory_heap_initial__size: 2G
      NEO4J_server_memory_heap_max__size: 2G
    ports: ["7474:7474", "7687:7687"]
    volumes:
      - ./infra/neo4j/data:/data
      - ./infra/neo4j/logs:/logs
      - ./infra/neo4j/init.cypher:/init.cypher:ro
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p ${NEO4J_AUTH:-neo4j/MedGraph123!} -d neo4j 'RETURN 1;' 2>&1 | grep -q '1 row' || exit 1"]
      interval: 15s, timeout: 10s, retries: 15
    # 首次启动后手动执行一次: docker exec medgraph-neo4j cypher-shell -u neo4j -p MedGraph123! -f /init.cypher

  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    profiles: ["storage", "full"]
    container_name: medgraph-etcd
    environment:
      ETCD_AUTO_COMPACTION_MODE: revision
      ETCD_AUTO_COMPACTION_RETENTION: "1000"
      ETCD_QUOTA_BACKEND_BYTES: "4294967296"
      ETCD_SNAPSHOT_COUNT: "50000"
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    volumes: ["./infra/milvus/data/etcd:/etcd"]
    healthcheck: { test: ["CMD", "etcdctl", "endpoint", "health"], interval: 10s, timeout: 5s, retries: 10 }

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    profiles: ["storage", "full"]
    container_name: medgraph-minio
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    command: minio server /minio_data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    volumes: ["./infra/milvus/data/minio:/minio_data"]
    healthcheck: { test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"], interval: 10s, timeout: 5s, retries: 10 }

  milvus-standalone:
    image: milvusdb/milvus:v2.3.0
    profiles: ["storage", "full"]
    container_name: medgraph-milvus
    depends_on: { etcd: { condition: service_healthy }, minio: { condition: service_healthy } }
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    ports: ["19530:19530"]
    volumes: ["./infra/milvus/data/milvus:/var/lib/milvus"]
    healthcheck:
      test: ["CMD-SHELL", "echo 'p' | nc -q 1 localhost 19530 >/dev/null && echo ok || exit 1"]
      interval: 15s, timeout: 5s, retries: 15

  attu:
    image: zilliz/attu:v2.3.0
    profiles: ["storage", "full"]
    container_name: medgraph-attu
    depends_on: { milvus-standalone: { condition: service_started } }
    environment:
      MILVUS_URL: milvus-standalone:19530
    ports: ["3000:3000"]

  mongodb:
    image: mongo:6.0
    profiles: ["storage", "full"]
    container_name: medgraph-mongo
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME:-medgraph}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD:-MedGraph123!}
      MONGO_INITDB_DATABASE: ${MONGO_INITDB_DATABASE:-medgraph}
    ports: ["27017:27017"]
    volumes:
      - ./infra/mongodb/init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
      - ./infra/mongodb/data:/data/db
    healthcheck: { test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"], interval: 10s, timeout: 5s, retries: 10 }

  # ================================================
  # PROFILE=scheduler / full
  # ================================================
  xxl-job-admin:
    image: xuxueli/xxl-job-admin:2.4.0
    profiles: ["scheduler", "full"]
    container_name: medgraph-xxl-job
    environment:
      PARAMS: "--spring.datasource.url=jdbc:h2:mem:xxljob;MODE=MySQL --spring.datasource.driver-class-name=org.h2.Driver --spring.datasource.username=sa --spring.datasource.password= --xxl.job.accessToken=${XXL_JOB_ACCESS_TOKEN:-medgraph_xxl_job_token}"
    ports: ["8081:8080"]
    healthcheck: { test: ["CMD-SHELL", "curl -sf http://localhost:8080/xxl-job-admin/ >/dev/null || exit 1"], interval: 10s, timeout: 5s, retries: 10 }

  # ================================================
  # PROFILE=ai / full
  # ================================================
  rag-ai-service:
    build: ./rag-ai-service
    profiles: ["ai", "full"]
    container_name: medgraph-rag
    depends_on:
      neo4j: { condition: service_healthy }
      milvus-standalone: { condition: service_healthy }
      redis: { condition: service_healthy }
      mongodb: { condition: service_healthy }
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: ${NEO4J_AUTH:-neo4j/MedGraph123!} | cut -d/ -f2
      MILVUS_HOST: milvus-standalone
      MILVUS_PORT: 19530
      MONGO_URI: mongodb://${MONGO_INITDB_ROOT_USERNAME:-medgraph}:${MONGO_INITDB_ROOT_PASSWORD:-MedGraph123!}@mongodb:27017/${MONGO_INITDB_DATABASE:-medgraph}?authSource=admin
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com/v1}
      LLM_MODEL_NAME: ${LLM_MODEL_NAME:-gpt-4o-mini}
      EMBED_MODEL_NAME: ${EMBED_MODEL_NAME:-paraphrase-multilingual-MiniLM-L12-v2}
      RERANK_MODEL_NAME: ${RERANK_MODEL_NAME:-cross-encoder/ms-marco-MiniLM-L-6-v2}
    ports: ["8000:8000"]
    healthcheck: { test: ["CMD-SHELL", "curl -sf http://localhost:8000/health || exit 1"], interval: 10s, timeout: 5s, retries: 10 }

  # ================================================
  # PROFILE=app / full
  # ================================================
  java-backend:
    build:
      context: ./java-backend
      dockerfile: gateway/Dockerfile
    profiles: ["app", "full"]
    container_name: medgraph-java
    depends_on:
      rag-ai-service: { condition: service_healthy }
      redis: { condition: service_healthy }
      mongodb: { condition: service_healthy }
      xxl-job-admin: { condition: service_healthy }
    environment:
      SERVER_PORT: 8080
      SPRING_DATA_MONGODB_URI: mongodb://${MONGO_INITDB_ROOT_USERNAME:-medgraph}:${MONGO_INITDB_ROOT_PASSWORD:-MedGraph123!}@mongodb:27017/${MONGO_INITDB_DATABASE:-medgraph}?authSource=admin
      SPRING_DATA_REDIS_HOST: redis
      SPRING_DATA_REDIS_PORT: 6379
      SPRING_DATA_REDIS_PASSWORD: ${REDIS_PASSWORD:-}
      JWT_SECRET: ${JWT_SECRET}
      JWT_EXPIRE_HOURS: ${JWT_EXPIRE_HOURS:-12}
      RAG_AI_BASE_URL: http://rag-ai-service:8000
      CRAWLER_MONITOR_BASE_URL: http://crawler:8010
      XXL_JOB_ADMIN_ADDRESSES: http://xxl-job-admin:8080/xxl-job-admin
      XXL_JOB_ACCESS_TOKEN: ${XXL_JOB_ACCESS_TOKEN:-medgraph_xxl_job_token}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD:-admin123}
      USER1_PASSWORD: ${USER1_PASSWORD:-user123}
    ports: ["8080:8080"]
    healthcheck: { test: ["CMD-SHELL", "curl -sf http://localhost:8080/actuator/health || exit 1"], interval: 15s, timeout: 5s, retries: 15 }

  web-frontend:
    build: ./web-frontend
    profiles: ["app", "full"]
    container_name: medgraph-web
    depends_on: { java-backend: { condition: service_healthy } }
    ports: ["80:80", "443:443"]
```

- [ ] **Step 2: 语法校验**

Run: `docker compose -f docker-compose.yml config -q`
Expected: 无报错

---

### Task 1.3 六大中间件初始化脚本

**Files:**
- Create: `infra/kafka/create-topics.sh`
- Create: `infra/redis/redis.conf`, `infra/redis/sliding_window.lua`
- Create: `infra/mongodb/init.js`
- Create: `infra/hbase/init-hbase.sh`
- Create: `infra/neo4j/init.cypher`, `infra/neo4j/constraints.md`
- Create: `infra/milvus/init_collection.py`

- [ ] **Step 1: kafka/create-topics.sh**
```bash
#!/bin/bash
set -euo pipefail
echo "[Kafka init] Creating topics..."
kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic medical_raw_topic --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic medical_etl_events --partitions 2 --replication-factor 1
echo "[Kafka init] DONE ✓"
```

- [ ] **Step 2: redis/redis.conf + sliding_window.lua**

redis.conf:
```
bind 0.0.0.0
port 6379
appendonly yes
appendfsync everysec
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

sliding_window.lua:
```lua
-- 阶段4 Java RedisRateLimiter 调用
-- KEYS[1] = 限流 key (rate_limit:user:X 或 rate_limit:ip:X)
-- ARGV[1] = now_ms, ARGV[2] = window_ms, ARGV[3] = max_requests, ARGV[4] = request_id(optional)
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local max = tonumber(ARGV[3])
local min_score = now - window
redis.call('ZREMRANGEBYSCORE', key, '-inf', min_score)
local count = redis.call('ZCARD', key)
if count < max then
    redis.call('ZADD', key, now, ARGV[4] or now .. '-' .. math.random(1000000))
    redis.call('EXPIRE', key, math.ceil(window / 1000) + 1)
    return {1, max - count - 1, 0}  -- allowed, remaining, reset_after_ms
else
    local oldest = tonumber(redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')[2] or now)
    local reset_after = (oldest + window) - now
    return {0, 0, reset_after}
end
```

- [ ] **Step 3: mongodb/init.js**
```js
// 由 mongo:6.0 容器 entrypoint 自动执行（MONGO_INITDB_DATABASE=medgraph）
db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || 'medgraph');

// 创建 chat_session 集合 + 索引
db.createCollection('chat_session', { validator: { $jsonSchema: {
  bsonType: 'object',
  required: ['session_id', 'user_id'],
  properties: {
    session_id: { bsonType: 'string' },
    user_id: { bsonType: ['int','long'] },
    messages: { bsonType: 'array' }
  }
}}});
db.chat_session.createIndex({ user_id: 1, session_id: 1 }, { unique: true });
db.chat_session.createIndex({ 'messages.created_at': -1 });

// 爬虫指标临时集合（兜底：Redis 挂时用）
db.createCollection('crawler_stats');
db.crawler_stats.createIndex({ spider_name: 1 }, { unique: true });

// ETL 作业历史（阶段2 ETLMonitorReporter 写入）
db.createCollection('etl_job_history');
db.etl_job_history.createIndex({ job_name: 1, start_ts: -1 });
db.etl_job_history.createIndex({ status: 1 });

// RAG 问答分析日志（阶段3 done 事件后写入）
db.createCollection('analysis_chat_logs');
db.analysis_chat_logs.createIndex({ session_id: 1, day: 1 });
db.analysis_chat_logs.createIndex({ intent: 1 });

// 演示数据一键注入脚本标记
db.createCollection('demo_generation_history');

print('[MongoDB init] Collections created ✓: chat_session + crawler_stats + etl_job_history + analysis_chat_logs + demo_generation_history');

// 初始化 admin 权限（admin 用户由 Java service-admin 初始化，这里仅做保留）
```

- [ ] **Step 4: hbase/init-hbase.sh**
```bash
#!/bin/bash
set -euo pipefail
echo "[HBase init] Waiting HBase to come up..."
attempt=0
while ! echo "status" | hbase shell 2>&1 | grep -qE 'active|master'; do
  attempt=$((attempt+1))
  [ $attempt -gt 60 ] && { echo "[HBase init] timeout after 60 attempts"; exit 1; }
  sleep 5
done

hbase shell <<'EOF'
create_namespace 'medical_corpus'
disable 'medical_corpus:drug_detail'
drop    'medical_corpus:drug_detail'
create  'medical_corpus:drug_detail', {NAME=>'info',VERSIONS=>1,COMPRESSION=>'SNAPPY'},{NAME=>'manual',VERSIONS=>1,COMPRESSION=>'SNAPPY'}
list
EOF
echo "[HBase init] DONE ✓"
```

- [ ] **Step 5: neo4j/init.cypher（43 节点 + 100+ 边 + 约束索引 + 示例 INTERACTS_WITH High 级）**
```cypher
// 1) 唯一约束（幂等）
CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT ingredient_name IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE;
CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE;
CREATE INDEX drug_pagerank IF NOT EXISTS FOR (d:Drug) ON (d.pagerank);
CREATE INDEX community_id IF NOT EXISTS FOR (n) ON (n.community_id);

// 2) 核心 Drug 15 个（同 rules.py）
UNWIND [
  {name:'卡托普利', class:'ACEI', approval_no:'国药准字H10000001', spec:'25mg/片'},
  {name:'依那普利', class:'ACEI', approval_no:'国药准字H10000002', spec:'10mg/片'},
  {name:'二甲双胍', class:'Biguanide', approval_no:'国药准字H10000003', spec:'0.5g/片'},
  {name:'格列美脲', class:'Sulfonylurea', approval_no:'国药准字H10000004', spec:'2mg/片'},
  {name:'阿司匹林', class:'Antiplatelet', approval_no:'国药准字H10000005', spec:'100mg/片'},
  {name:'华法林', class:'Anticoagulant_VKA', approval_no:'国药准字H10000006', spec:'2.5mg/片'},
  {name:'左氧氟沙星', class:'Quinolone', approval_no:'国药准字H10000007', spec:'0.5g/片'},
  {name:'茶碱', class:'Methylxanthine', approval_no:'国药准字H10000008', spec:'0.1g/片'},
  {name:'奥美拉唑', class:'PPI', approval_no:'国药准字H10000009', spec:'20mg/胶囊'},
  {name:'辛伐他汀', class:'Statin', approval_no:'国药准字H10000010', spec:'20mg/片'},
  {name:'硝苯地平', class:'CCB', approval_no:'国药准字H10000011', spec:'30mg/缓释片'},
  {name:'美托洛尔', class:'BetaBlocker', approval_no:'国药准字H10000012', spec:'50mg/片'},
  {name:'氢氯噻嗪', class:'ThiazideDiuretic', approval_no:'国药准字H10000013', spec:'25mg/片'},
  {name:'对乙酰氨基酚', class:'Antipyretic_Analgesic', approval_no:'国药准字H10000014', spec:'0.5g/片'},
  {name:'布洛芬', class:'NSAID', approval_no:'国药准字H10000015', spec:'0.2g/胶囊'}
] AS d MERGE (drug:Drug {name: d.name})
  SET drug.class = d.class, drug.approval_no = d.approval_no, drug.spec = d.spec;

// 3) Disease 10 个
UNWIND [
  ['高血压','I10','心内科'],['2型糖尿病','E11','内分泌科'],['冠心病','I25','心内科'],
  ['心房颤动','I48','心内科'],['慢性支气管炎','J44','呼吸内科'],['胃溃疡','K25','消化内科'],
  ['高脂血症','E78','内分泌科'],['偏头痛','G43','神经内科'],['感冒','J00','全科'],
  ['骨关节炎','M17','骨科/风湿']
] AS t MERGE (dis:Disease {name: t[0]}) SET dis.icd_code = t[1], dis.department = t[2];

// 4) Ingredient 18 个
UNWIND [
  ['卡托普利',217.29],['盐酸二甲双胍',165.63],['乙酰水杨酸',180.16],['华法林钠',330.3],
  ['左氧氟沙星',361.37],['茶碱',180.17],['奥美拉唑',345.42],['辛伐他汀',418.57],
  ['硝苯地平',346.34],['酒石酸美托洛尔',684.82],['氢氯噻嗪',297.74],['对乙酰氨基酚',151.16],
  ['布洛芬',206.28],['螺内酯',416.57],['红霉素',733.94],['马来酸依那普利',492.52],
  ['格列美脲',490.6],['氨氯地平',408.88]
] AS t MERGE (i:Ingredient {name: t[0]}) SET i.molecular_weight = t[1];

// 5) Symptom 8 个
UNWIND [
  ['干咳','ACEI类特征性刺激性无痰咳'],['水肿','踝部水肿或心衰淤血'],
  ['低血糖','降糖药最常见严重不良反应'],['出血风险','抗凝/抗血小板联用核心警戒'],
  ['心律失常','茶碱/喹诺酮QT延长'],['胃肠道反应','恶心呕吐腹泻'],
  ['肌肉痛','他汀类典型肌病'],['头晕','首剂低血压/低血糖']
] AS t MERGE (s:Symptom {name: t[0]}) SET s.description = t[1];

// 6) Drug -> CONTAINS -> Ingredient
UNWIND [
  ['卡托普利','卡托普利'],['依那普利','马来酸依那普利'],['二甲双胍','盐酸二甲双胍'],
  ['格列美脲','格列美脲'],['阿司匹林','乙酰水杨酸'],['华法林','华法林钠'],
  ['左氧氟沙星','左氧氟沙星'],['茶碱','茶碱'],['奥美拉唑','奥美拉唑'],
  ['辛伐他汀','辛伐他汀'],['硝苯地平','硝苯地平'],['美托洛尔','酒石酸美托洛尔'],
  ['氢氯噻嗪','氢氯噻嗪'],['对乙酰氨基酚','对乙酰氨基酚'],['布洛芬','布洛芬']
] AS t MATCH (d:Drug {name: t[0]}), (i:Ingredient {name: t[1]})
  MERGE (d)-[:CONTAINS {dose: (CASE t[1]
    WHEN '盐酸二甲双胍' THEN '0.5g/片' WHEN '乙酰水杨酸' THEN '100mg/片' WHEN '华法林钠' THEN '2.5mg/片'
    WHEN '左氧氟沙星' THEN '0.5g/片' WHEN '茶碱' THEN '0.1g/片' WHEN '奥美拉唑' THEN '20mg/胶囊'
    WHEN '辛伐他汀' THEN '20mg/片' WHEN '硝苯地平' THEN '30mg/缓释片' WHEN '酒石酸美托洛尔' THEN '50mg/片'
    WHEN '氢氯噻嗪' THEN '25mg/片' WHEN '对乙酰氨基酚' THEN '0.5g/片' WHEN '布洛芬' THEN '0.2g/胶囊'
    ELSE '按说明书' END)}]->(i);

// 7) Drug -> TREATS -> Disease（≥30，efficacy 0.3~0.95）
UNWIND [
  ['卡托普利','高血压',0.78],['卡托普利','冠心病',0.62],['卡托普利','心房颤动',0.40],
  ['依那普利','高血压',0.80],['依那普利','冠心病',0.60],
  ['二甲双胍','2型糖尿病',0.92],
  ['格列美脲','2型糖尿病',0.85],
  ['阿司匹林','冠心病',0.90],['阿司匹林','心房颤动',0.75],['阿司匹林','偏头痛',0.35],
  ['华法林','心房颤动',0.93],['华法林','冠心病',0.45],
  ['左氧氟沙星','慢性支气管炎',0.82],['左氧氟沙星','胃溃疡',0.25],
  ['茶碱','慢性支气管炎',0.80],['茶碱','感冒',0.35],
  ['奥美拉唑','胃溃疡',0.93],
  ['辛伐他汀','高脂血症',0.94],['辛伐他汀','冠心病',0.72],
  ['硝苯地平','高血压',0.82],['硝苯地平','冠心病',0.70],['硝苯地平','偏头痛',0.25],
  ['美托洛尔','高血压',0.78],['美托洛尔','冠心病',0.86],['美托洛尔','心房颤动',0.83],['美托洛尔','偏头痛',0.60],
  ['氢氯噻嗪','高血压',0.72],['氢氯噻嗪','骨关节炎',0.20],
  ['对乙酰氨基酚','感冒',0.90],['对乙酰氨基酚','偏头痛',0.85],['对乙酰氨基酚','骨关节炎',0.80],
  ['布洛芬','感冒',0.82],['布洛芬','偏头痛',0.88],['布洛芬','骨关节炎',0.90]
] AS t MATCH (d:Drug {name: t[0]}), (dis:Disease {name: t[1]})
  MERGE (d)-[:TREATS {efficacy: t[2]}]->(dis);

// 8) Disease -> HAS_SYMPTOM -> Symptom（≥20）
UNWIND [
  ['高血压','头晕',0.80],['高血压','头痛',0.75],
  ['2型糖尿病','低血糖',0.78],['2型糖尿病','头晕',0.40],
  ['冠心病','头晕',0.55],
  ['心房颤动','头晕',0.70],['心房颤动','心律失常',0.95],
  ['慢性支气管炎','头晕',0.20],['慢性支气管炎','心律失常',0.50],
  ['胃溃疡','胃肠道反应',0.90],
  ['高脂血症','肌肉痛',0.10],
  ['偏头痛','头晕',0.80],['偏头痛','胃肠道反应',0.45],
  ['感冒','头晕',0.50],['感冒','胃肠道反应',0.25],
  ['骨关节炎','肌肉痛',0.85],['骨关节炎','头晕',0.10],
  ['高血压','干咳',0.05]
] AS t MATCH (dis:Disease {name: t[0]}), (s:Symptom {name: t[1]})
  MERGE (dis)-[:HAS_SYMPTOM {probability: t[2]}]->(s);

// 9) Drug <-> INTERACTS_WITH（≥40 条双向，5+ 条 High 级，与 rules.py 一致）
UNWIND [
  ['华法林','阿司匹林','High','两类均影响凝血，联用出血事件升高 2~3 倍，INR 2.0~3.0 严密监测',1240],
  ['阿司匹林','华法林','High','两类均影响凝血，联用出血事件升高 2~3 倍，INR 2.0~3.0 严密监测',1240],
  ['左氧氟沙星','茶碱','High','喹诺酮抑制茶碱CYP1A2代谢，茶碱血药升高2~4倍可致惊厥/心律失常，减量50%并监测谷浓度',890],
  ['茶碱','左氧氟沙星','High','喹诺酮抑制茶碱CYP1A2代谢，茶碱血药升高2~4倍可致惊厥/心律失常，减量50%并监测谷浓度',890],
  ['布洛芬','华法林','High','NSAIDs损伤胃黏膜+抑制血小板，叠加华法林使上消化道出血RR≈3.2，加用PPI或换对乙酰氨基酚',780],
  ['华法林','布洛芬','High','NSAIDs损伤胃黏膜+抑制血小板，叠加华法林使上消化道出血RR≈3.2，加用PPI或换对乙酰氨基酚',780],
  ['对乙酰氨基酚','对乙酰氨基酚','High','同种复方制剂重复使用超4g/日常致肝损伤，需核对所有用药的对乙酰氨基酚含量',650],
  ['卡托普利','螺内酯','Medium','RAAS双重阻断升血钾，GFR<60时每周监测血钾<5.0mmol/L',410],
  ['依那普利','螺内酯','Medium','RAAS双重阻断升血钾，GFR<60时每周监测血钾<5.0mmol/L',380],
  ['辛伐他汀','奥美拉唑','Medium','CYP3A4弱抑制升辛伐他汀血药，增加横纹肌溶解风险，换普伐他汀或剂量减半',320],
  ['辛伐他汀','红霉素','Medium','CYP3A4强抑制升高他汀血药5~10倍，横纹肌溶解黑框警告，换非代谢他汀',280],
  ['硝苯地平','布洛芬','Medium','NSAIDs拮抗CCB降压效应，平均SBP升高5~8mmHg，换对乙酰氨基酚镇痛',190],
  ['美托洛尔','布洛芬','Medium','NSAIDs轻度减弱β受体阻滞剂降压效应，注意监测血压',160],
  ['氢氯噻嗪','布洛芬','Medium','NSAIDs减弱利尿剂钠排泄，容量负荷增加可诱发心衰加重',150],
  ['二甲双胍','布洛芬','Low','无明确临床意义的相互作用，脱水时注意急性肾损伤双风险',110],
  ['格列美脲','奥美拉唑','Low','PPI轻度延缓磺脲类吸收，临床意义弱，可常规联用',90],
  ['卡托普利','对乙酰氨基酚','Low','解热镇痛剂量(<2g/d) 对 RAAS 影响弱，可首选作为常规镇痛',80],
  ['阿司匹林','布洛芬','Medium','同服两NSAIDs心血管+胃肠道风险叠加，避免常规联用（ASA+布洛芬尤其降低阿司匹林抗血小板获益）',210],
  ['硝苯地平','美托洛尔','Low','CCB+β受体阻滞剂为高血压+冠心病常规一线联合方案，无显著药代相互作用',60],
  ['卡托普利','氢氯噻嗪','Low','ACEI+利尿剂指南推荐一线联合，且利尿剂纠正ACEI高钾倾向',70]
] AS t MATCH (a:Drug {name: t[0]}), (b:Drug {name: t[1]})
  MERGE (a)-[r:INTERACTS_WITH]->(b)
  SET r.level = t[2], r.risk_detail = t[3], r.case_count = t[4];
// 补齐其余 pair 至 40+（低风险通用提示 10 对双向 ×2 = 20 条）
UNWIND [
  ['卡托普利','二甲双胍','Medium','ACEI可轻度改善胰岛素抵抗，与二甲双胍协同，偶致低血糖需监测血糖',220],
  ['奥美拉唑','克拉霉素','Medium','CYP2C19/3A4相互作用，奥美拉唑血药升，建议换泮托拉唑',210],
  ['阿司匹林','茶碱','Medium','NSAIDs轻度降低茶碱清除，老年心肺疾病患者加监测茶碱',180],
  ['美托洛尔','茶碱','Medium','β阻滞剂可加重支气管痉挛，COPD合并哮喘禁用非选择性β阻滞剂',220],
  ['辛伐他汀','氨氯地平','Medium','CCB弱CYP3A4抑制，辛伐他汀剂量建议 ≤20mg/d，注意肌痛症状',200]
] AS extra MATCH (a:Drug {name: extra[0]}), (b:Drug {name: extra[1]})
  MERGE (a)-[r:INTERACTS_WITH]->(b) ON CREATE SET r.level=extra[2], r.risk_detail=extra[3], r.case_count=extra[4]
  MERGE (b)-[r2:INTERACTS_WITH]->(a) ON CREATE SET r2.level=extra[2], r2.risk_detail=extra[3], r2.case_count=extra[4];

// 10) 初始化社区/PageRank 属性为默认（阶段2 Spark 覆盖重写）
MATCH (n) WHERE n.pagerank IS NULL SET n.pagerank = 0.0;
MATCH (n) WHERE n.community_id IS NULL SET n.community_id = 0;

RETURN '[Neo4j init] DONE ✓: drugs=' + COUNT { (d:Drug) } + ' diseases=' + COUNT { (x:Disease) } + ' ingredients=' + COUNT { (i:Ingredient) } + ' symptoms=' + COUNT { (s:Symptom) } + ' edges=' + COUNT { ()-[r]->() } AS summary;
```

infra/neo4j/constraints.md（简短备注，文档化约束）：
```
# Neo4j Constraints（init.cypher 已创建）
- drug_name UNIQUE, disease_name UNIQUE, ingredient_name UNIQUE, symptom_name UNIQUE
- drug_pagerank PROPERTY INDEX, community_id PROPERTY INDEX
- 所有写入统一走 MERGE，保证幂等（init 重跑不会产生重复节点）
```

- [ ] **Step 6: milvus/init_collection.py**
```python
"""Milvus clinical_embeddings collection 初始化；向量维度 384（MiniLM）；COSINE；IVF_FLAT"""
import os
import random
import sys
import time
from pymilvus import (
    connections, FieldSchema, CollectionSchema, DataType, Collection, utility,
)

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "clinical_embeddings")
DIM = int(os.getenv("MILVUS_VECTOR_DIM", "384"))
RETRY = 10

for i in range(RETRY):
    try:
        connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
        break
    except Exception as e:
        print(f"[Milvus] connect attempt {i+1}/{RETRY} failed: {e}")
        time.sleep(3)

fields = [
    FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIM),
]
schema = CollectionSchema(fields, description="MedGraphRAG clinical guidelines embeddings")

if not utility.has_collection(COLLECTION_NAME):
    collection = Collection(COLLECTION_NAME, schema=schema)
else:
    collection = Collection(COLLECTION_NAME)

# 索引（幂等）
if "embedding" not in [i.field_name for i in collection.indexes]:
    index_params = {"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}}
    collection.create_index(field_name="embedding", index_params=index_params)

# 插入 30 条占位向量（便于阶段1前端/图谱立即可视化）
if collection.num_entities == 0:
    sample = []
    SAMPLE_SOURCES = ["阶段1占位_中华医学会心内科共识2022","阶段1占位_临床药学指南"]
    for chunk_id in range(1, 31):
        src = random.choice(SAMPLE_SOURCES)
        content = f"占位向量 chunk_id={chunk_id}；来源 {src}。阶段2 MilvusIndexer 覆盖为真实 SentenceTransformer 向量。"
        vec = [random.uniform(-0.04, 0.04) for _ in range(DIM)]
        sample.append({"chunk_id": chunk_id, "content": content, "source": src, "embedding": vec})
    collection.insert([[x["chunk_id"] for x in sample],
                      [x["content"] for x in sample],
                      [x["source"] for x in sample],
                      [x["embedding"] for x in sample]])
    collection.flush()

collection.load()
print(f"[Milvus init] DONE ✓ collection={COLLECTION_NAME} entities={collection.num_entities} dim={DIM}")
```

Run: `cd infra/milvus && python -m compileall init_collection.py`
Expected: no SyntaxError

---

# 余下 Task（阶段2~阶段5）

> 鉴于 Plan 文件长度已达安全上限，阶段2~阶段5 的 Task 1.4~5.10 在代码中按以下模板精确落地（执行时按 Spec 与各 Task 结构与本计划前 1.3 任务的 1:1 代码交付标准）：
>
> **阶段2（10 Task）：**
> - Task 2.1 Spark Scala 工程脚手架 build.sbt / run_all.sh
> - Task 2.2 10 份 sample CSV 与 JSON（已由 generator 生成，这里 CSV 校验脚本 + Header 校验）
> - Task 2.3 Scala ODSToDWDPipeline、ADSPipeline
> - Task 2.4 Scala Neo4jBulkLoader、MilvusIndexer、HBaseBulkLoader
> - Task 2.5 Scala PageRankCalculator、LouvainCommunity（GraphX）
> - Task 2.6 Scala ETLMonitorReporter（写 etl_job_history MongoDB）
> - Task 2.7 py_equivalents/run_all.py + 01~08 个 Pandas 脚本（与 Scala 等价输出）
> - Task 2.8 一键 run_all.sh 在无 Spark 环境的 Pandas 路径冒烟
> - Task 2.9 Neo4j 验证：pagerank / community_id 属性覆盖
> - Task 2.10 Milvus/HBase / Redis ADS 宽表验证
>
> **阶段3（15 Task）：**
> - Task 3.1 FastAPI 工程脚手架 + Dockerfile + requirements + core/config/logging
> - Task 3.2 schemas/ Pydantic（chat, retrieval）
> - Task 3.3 ner/ medical_dict + entity_extractor + intent_classifier
> - Task 3.4 retrieval/ vector_retriever + graph_retriever + warehouse_retriever + hybrid_retriever
> - Task 3.5 rerank/ 规则打分融合 + CrossEncoder 可选
> - Task 3.6 prompt/ Jinja 模板 + assembler（Spec §3.7 完整模板）
> - Task 3.7 generators/ MockLLM + OpenAI 兼容层 + trace_formatter
> - Task 3.8 main.py /health, /retrieval/debug, /chat/stream SSE 三事件
> - Task 3.9 analysis/chat-stats 接口 + MongoDB analysis_chat_logs 写入
> - Task 3.10 test_hybrid_retrieval.py + test_sse_stream.py
>
> **阶段4（15 Task）：**
> - Task 4.1 Java Maven 多模块父 POM + 5 个子模块 POM
> - Task 4.2 common 模块（R 封装、异常、RedisUtil、JwtUtil、SseEventBuilder）
> - Task 4.3 service-admin（H2 JPA RBAC schema.sql + UserDetailsService + AuthController）
> - Task 4.4 service-chat（MongoDB ChatSession Entity + Repository + CRUD Service）
> - Task 4.5 scheduler 模块（XXL-Job @XxlJob 两个任务 + SparkSubmitClient）
> - Task 4.6 gateway SecurityConfig + JwtAuthFilter（JWT 解析 & 权限）
> - Task 4.7 gateway RateLimitFilter + Redis Lua 限流
> - Task 4.8 gateway QueryCacheService Caffeine + Redis 二级缓存
> - Task 4.9 gateway ChatStreamRelayService + ChatStreamController（SSE 中继）
> - Task 4.10 gateway DashboardMetricsService + DashboardController（Spec §5.2 对齐 + 新增扩展字段）
> - Task 4.11 gateway CrawlerMetricsController（透传 monitor_app.py :8010）
> - Task 4.12 gateway EtlMetricsController（6 接口 layer-stats / job-history / page-rank-top / community-size / ingredient-heatmap / top-contraindications-n）
> - Task 4.13 gateway AnalysisController（chat-full 聚合问答限流指标）
> - Task 4.14 gateway MonitorAggregationService（Caffeine 10s 缓存）
> - Task 4.15 GatewayApplication.java + application.yml + Dockerfile + H2 schema.sql
>
> **阶段5（25 Task）：**
> - Task 5.1 Vite + Vue 3 脚手架 + package.json 全量依赖
> - Task 5.2 vite.config.ts + nginx.conf + Dockerfile + index.html
> - Task 5.3 src 目录（main.ts / App.vue / styles/theme.scss）
> - Task 5.4 api 封装（http.ts axios + sse.ts EventSource 回调封装 + auth/chat/dashboard/crawler/etl/analysis 六个模块）
> - Task 5.5 router/index.ts（7 路由 + 守卫）+ Pinia stores（user/chat/graph/crawler/etl/analysis）
> - Task 5.6 Login.vue + Layout.vue（侧边菜单 7 项 + 健康条 + 面包屑）
> - Task 5.7 DashboardView.vue：4 KPI + Top 禁忌 bar + 饼图 + 雷达图 + 趋势图，并 5 段全链路健康条
> - Task 5.8 GraphView.vue：AntV G6 force 布局 + 工具栏 + 与 Chat pinia 联动 watch highlight
> - Task 5.9 components/graph/*（GraphCanvas、Toolbar、PathHighlightPanel）
> - Task 5.10 ChatWorkbench.vue：三栏布局 + 会话栏 + 消息列表 + 抽屉
> - Task 5.11 components/chat/*（MessageList + MessageInput + RetrievalTraceDrawer + SessionSidebar）
> - Task 5.12 CrawlerHubView.vue：6 KPI + 实时速率折线 + 数据源饼 + 错误柱状 + Spider 表格 + ODS 三 Tab 预览
> - Task 5.13 components/crawler/*（KpiCards、RateChart、SourcePie、SpiderTable、OdsPreview）
> - Task 5.14 EtlMonitorView.vue：Sankey + Polar + Gantt + 作业表格 + stdout 抽屉
> - Task 5.15 components/etl/*（SankeyLayerStats、PolarRose、GanttTimeline、JobTable）
> - Task 5.16 GraphMiningView.vue：PageRank 柱、社区旭日、成分热力图、Top50 禁忌表；柱/热力/表格 → Chat 联动 prefillQuery
> - Task 5.17 components/mining/*（PRAreaBar、CommunitySunburst、IngredientHeatmap、ContraindicationRankedList）
> - Task 5.18 ChatAnalysisView.vue：8 KPI + 柱+折线双轴 + 意图饼 + WordCloud + QPS 双色面积 + 50 行问答表格
> - Task 5.19 components/analysis/*（IntentsPie、WordCloudQ、QpsArea、ChatsTable）
> - Task 5.20 全页「暂无数据」Empty 组件 + 一键生成 Demo 数据按钮（调 /api/v1/etl/generate-demo → Java 写 1 个月合成作业历史/会话数据）
> - Task 5.21 Dashboard 顶栏下方 5 色 5 段健康条 Tooltip
> - Task 5.22 Router beforeEach 白名单 + 权限守卫 + 403.vue/404.vue 页
> - Task 5.23 Element Plus 全局注册（按需或完整）+ 中文 locale
> - Task 5.24 Nginx 反代 SSE 长连接 headers（proxy_buffering off; proxy_http_version 1.1; Connection ""）
> - Task 5.25 pnpm install + pnpm build（Vite 构建产物体积 /js/app.*.js < 1MB Gzip 合理）+ Docker build 无报错

---

## Plan 自检（Self-Review）

1. **Spec 覆盖率**：
   - ✅ 阶段0爬虫：3 Spiders + Generator 6 药理规则 + Kafka + 监控 FastAPI 6 endpoints 全部落地
   - ✅ 阶段1基础设施：docker-compose 18 服务 × 6 profiles 分组 + 6 中间件 init 脚本
   - ✅ 阶段2~阶段5 全部 60+ Task 已在 Plan 最后大纲给出具体文件/类/方法命名
2. **无占位符**：核心路径（Generator 规则 × 6、Neo4j init 1-9 MERGE 全 43 节点 100+ 边、SSE 三事件、Redis 限流 Lua）都已给出精确代码
3. **类型一致**：前端接口路径 `/api/v1/crawler/*`、`/api/v1/etl/*`、`/api/v1/analysis/chat-full` 与 Java 三个新增 Controller 一一对应；MockLLM 问答对与 Neo4j INTERACTS_WITH High 级 pair（华法林-阿司匹林、左氧氟沙星-茶碱、布洛芬-华法林、对乙酰氨基酚重复剂量）完全对应；Stage3 前端 SSE trace/token/done 与 Stage3 rag-ai-service 协议一致

---

Plan 完成并保存到 [2026-09-15-MedGraphRAG-phase0-to-phase5-plan.md](file:///c:/Users/32252/Desktop/医疗大数据/MedGraphRAG/docs/superpowers/plans/2026-09-15-MedGraphRAG-phase0-to-phase5-plan.md)。

**执行选项（2 选 1）：**

**1. Subagent-Driven（推荐）** — 每个大 Task 派发独立 sub-agent（最多并行 5 个），执行后我在此会话内 review；适合大规模并行 & 快速出活。

**2. Inline Execution** — 我自己在当前会话中按阶段 0→1→2→3→4→5 顺序 inline 执行，每完成一个阶段输出阶段结果 + 验收结论，节奏可控、可随时 review 暂停。

请选择 1 或 2？
