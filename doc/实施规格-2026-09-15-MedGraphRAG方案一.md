# MedGraphRAG 实施规格（方案一：分层渐进式 + 爬虫采集 + 可视化增强）

> 配套主设计文档：[设计文档.md](./设计文档.md)
> 方案选择：方案一（分层渐进式，自底向上 6 阶段）
> 前端框架：Vue 3 + Element Plus + ECharts + AntV G6 + AntV G2Plot + WordCloud
> 依赖策略：Docker Compose 全栈编排（12+ 容器中间件 + 自动初始化）
> LLM 策略：OpenAI 协议兼容层 + MockLLM 兜底（无 Key 可演示）
> 爬虫策略：Scrapy 双模式（真实采集 CMeKG 等公开源 + 高质量模拟数据生成器兜底）

---

## 0. 实施总览

| 阶段 | 名称 | 核心交付物 | 验收方式 |
|------|------|-----------|---------|
| **阶段0** | **爬虫数据采集层** | **Scrapy 项目 3 爬虫 + Kafka Producer + 采集监控 FastAPI + 模拟数据生成器；输出 ODS 原始 JSON/CSV** | **启动爬虫 → Kafka 有消息 → 前端数据采集中枢可见实时采集速率 & 累计量** |
| 阶段1 | 基础设施层 | docker-compose.yml、各中间件 init 脚本、.env.example | `docker-compose up` 后所有 Web UI 可访问、示例数据已自动注入 |
| 阶段2 | 数据层与图谱构建 | Spark Scala 作业 x7（+ Python pandas 等价脚本）、示例 CSV x10、Neo4j 图谱 PageRank/Community 回写、Milvus/HBase 装载完成 | spark-submit 成功跑完作业链，Neo4j Browser 可见节点属性 pagerank & community_id |
| 阶段3 | AI 计算中枢 | Python FastAPI 服务、NER/三路检索/Rerank/Prompt/流式生成、SSE 三事件协议 | curl SSE 端点依次收到 trace → token*N → done |
| 阶段4 | Java 后端中枢 | Spring Boot 多模块 Maven 工程、JWT/RBAC、Redis 限流、Caffeine+Redis 二级缓存、SSE 中继、XXL-Job 调度、大屏接口 + 爬虫/ETL/问答分析指标接口 | 登录获取 JWT → 调 SSE 接口看到 Java 侧转发的 token 流；Dashboard 接口返回 JSON 含新增可视化字段 |
| 阶段5 | 前端展现层（可视化增强） | **Vue 3 工程：Login + 数据采集中枢 + 数仓ETL看板 + 图挖掘分析页 + 问答效果分析 + Dashboard大屏 + Graph图谱 + Chat工作台 + Nginx** | **浏览器访问 → 6 大主页面全部有数据有图表，爬虫/ETL/问答数据全链路可追踪可视化** |

---

## A. 阶段0 — 爬虫数据采集层（Python Scrapy + Kafka + 采集监控）

### A.1 模块结构（新增 `data-crawler/` 目录）

```
data-crawler/
├── requirements.txt
│   ├── scrapy==2.11.0, scrapy-redis==0.8.0     # Scrapy 核心（分布式可选）
│   ├── kafka-python==2.0.2                     # Kafka Producer 推送 raw topic
│   ├── fake==18.11.2, openpyxl==3.1.2          # 模拟数据生成器依赖
│   ├── fastapi==0.110.0, uvicorn==0.27.1       # 采集监控 & 手动触发 API
│   ├── pydantic==2.6.1, loguru==0.7.2
│   └── jieba==0.42.1, pypinyin==0.50.0         # 中文医学文本处理
├── Dockerfile                                  # 基于 python:3.10-slim，可选挂到 compose
├── run.sh                                      # 一键入口：scrapy crawlall 或 generator
├── monitor_app.py                              # 采集监控 FastAPI (端口 8010)
│
├── medical_crawler/                            # Scrapy 项目根
│   ├── scrapy.cfg
│   ├── settings.py                             # PIPELINES 配置 → KafkaProducerPipeline / JsonLinesWriterPipeline
│   ├── items.py                                # DrugRawItem / DiseaseRawItem / GuidelineRawItem（Scrapy Item）
│   ├── pipelines.py
│   │   ├── KafkaProducerPipeline               #   清洗基本字段 → push kafka medical_raw_topic
│   │   ├── JsonLinesWriterPipeline             #   同时落盘到 data-crawler/output/ods_raw/*.jsonl（离线备份）
│   │   └── StatsCollectorPipeline              #   Redis 计数（per-spider 已采集条数）
│   ├── middlewares.py
│   └── spiders/
│       ├── cmekg_spider.py                     #   Spider 1: CMeKG 医药知识库公开数据抓取（CMeKG 官方开放 API 或 dump）
│       ├── drug_label_spider.py                #   Spider 2: 国家药监局药品说明书公开数据抓取
│       └── clinical_guideline_spider.py        #   Spider 3: 临床指南/专家共识公开页面抓取
│
├── generator/                                  # 模拟数据生成器（真实站点抓取失败时的兜底方案）
│   ├── drug_generator.py                       #   基于 15 核心药品 → 扩展到 100~200 条合成药品
│   ├── disease_generator.py                    #   10 疾病 → 扩展到 50 条合成疾病
│   ├── interaction_generator.py                #   药物相互作用合成（基于真实药理规则组合）
│   └── guideline_generator.py                  #   临床指南片段合成（基于模板 + 同义词替换）
│
├── output/
│   └── ods_raw/                                #   ODS 原始数据落盘（与 spark-jobs/data/sample 做软链，供阶段2直接读）
│
└── tests/
    ├── test_items.py
    └── test_generator_rules.py                 #   验证生成的药物相互作用不矛盾、符合药理规则
```

### A.2 三个目标爬虫设计（真实采集 + 双模式切换）

| 爬虫名 | 数据源 | 抓取策略 | 输出 Item（对齐设计文档 ODS 层 §3.1） |
|--------|--------|---------|--------------------------------------|
| cmekg_spider | CMeKG (Chinese Medical Knowledge Graph) 官方开放下载 / 公开 API | 优先读取公开 dump JSON，无法访问时走 HTTP API 分页，间隔 1s，自动重试 3 次 | `DiseaseRawItem(disease_id, name, icd_code, aliases[], department, symptoms[], treatments[])` |
| drug_label_spider | 国家药监局 NMPA 药品信息公开查询 / Drugs.com 中文镜像 | 列表页分页（每页 20 条，限前 50 页 = 1000 条），详情页解析批准文号/通用名/规格/用法用量/禁忌/药理作用 | `DrugRawItem(drug_id, name, approval_no, dosage_form, spec, usage, adverse_reaction, contraindication_text, pharmacology_text, ingredients[])` |
| clinical_guideline_spider | 中华医学会临床指南 / 医脉通公开指南页面 | 关键词检索抓取，按「高血压、糖尿病、冠心病、…」10 个病种检索，每个病种取前 10 篇，TextSplitter 切 500 字 chunk | `GuidelineRawItem(chunk_id, content, source, publish_year, drug_refs[], disease_refs[])` |

**双模式开关**（data-crawler/settings.py）：
```python
# CRAWL_MODE = "real" → 真实爬取，失败 5 次后单页跳过并 warn
# CRAWL_MODE = "mock" → 全部跳过真实抓取，直接调 generator 生成
# CRAWL_MODE = "hybrid"（默认）→ 先尝试 real，失败超阈值则 fallback generator
CRAWL_MODE = os.getenv("CRAWLER_MODE", "hybrid")
FALLBACK_THRESHOLD = 10  # 连续失败 10 页 → 当前 spider 切 mock
```

### A.3 Kafka 接入 + ODS 落盘（与设计文档第 2 节数据接入层对齐）

```python
# pipelines.py KafkaProducerPipeline
class KafkaProducerPipeline:
    """每条 Item → Kafka message, key=spider_name, value=json(item)"""
    TOPIC = "medical_raw_topic"  # 阶段1 kafka create-topics.sh 已创建
    def process_item(self, item, spider):
        msg = {
            "ods_type": spider.name,          # cmekg / drug_label / guideline
            "ts": int(time.time() * 1000),
            "payload": dict(item),
        }
        self.producer.send(self.TOPIC, key=spider.name.encode(), value=orjson.dumps(msg))
        # 同时写本地 output/ods_raw/{spider}.jsonl → 软链到 spark-jobs/data/sample/
        self.local_writer.writeline(json.dumps(msg, ensure_ascii=False))
```

Kafka topic → 后续可被 Spark Structured Streaming 消费入 ODS Hive 表；当前阶段先落盘为 JSONL，阶段2 Spark SQL 直接 `spark.read.json("output/ods_raw/*.jsonl")` 即可。

### A.4 模拟数据生成器（generator/）设计规则（保障医学合理性，不瞎生成）

**drug_generator.py 核心规则：**
- 基础药品模板 15 个 → 名称合成：{前缀}{成分缩写}{剂型后缀}（例：盐酸{二甲双胍}{缓释片}、{左旋}{氨氯地平}{胶囊}）
- 批准文号：国药准字 + H + 8位递增
- 适应症/禁忌：从模板池按类别随机组合（降压药适应症必含「高血压」，ACEI 禁忌必含「双侧肾动脉狭窄」）
- 成分关联：每个合成药 1~3 种成分；成分池复用阶段2 10 核心成分 + 扩展 40 种常见成分

**interaction_generator.py 药理规则（关键：不矛盾）：**
```
规则库（举例 6 条）：
R1. 任何「抗凝/抗血小板」类药物两两组合 → level=High, risk=出血风险显著增加
R2. 喹诺酮类（左氧/环丙）+ 茶碱类 → level=High, risk=茶碱代谢抑制，血药浓度升高致心律失常
R3. NSAIDs（布洛芬/对乙酰氨基酚剂量 ≥2g/日）+ 华法林 → level=High, risk=胃肠道出血
R4. ACEI（卡托普利/依那普利）+ 螺内酯 → level=Medium, risk=高钾血症
R5. 他汀类（辛伐他汀）+ CYP3A4 强抑制剂（奥美拉唑/红霉素）→ level=Medium, risk=横纹肌溶解
R6. 同通用名不同商品名 → level=High, risk=重复用药过量
→ 按 R1~R6 生成 500+ 条合成相互作用，且保证 drug_a ↔ drug_b 双向一致
```

**guideline_generator.py：** 20+ 模板句式 × 10 病种 × 5 种药物类别 = 1000+ 合成 chunk，关键词替换保证内容不重复，关键引用（「证据等级 A」「推荐强度 I 类」）符合真实指南写作风格。

### A.5 采集监控 FastAPI（monitor_app.py :8010）

前端数据采集中枢页面的后端数据来源：

```
GET  /crawler/health           → {"status":"ok","mode":"hybrid","kafka_connected":true}
GET  /crawler/stats            → 每个 spider 的 {spider_name, total_items, rate_per_min, last_10_min_trend[], errors, avg_latency_ms}
                                 + 今日累计 / 昨日对比 + Kafka topic lag（消费端=Spark 未接时 lag 会涨，前端显示告警）
GET  /crawler/sources          → 3 个数据源的 {name, last_fetch_ts, health_score(0~100), records_fetched} 饼图数据
POST /crawler/spider/{name}/run  → 手动触发单个 spider 立即跑一轮
POST /crawler/generator/run    → 手动触发模拟数据生成（刷新 ODS）
GET  /crawler/ods_preview?type=drug&limit=10  → 最新 10 条 ODS 原始数据 JSON（前端 Table 预览）
```

采集进度存 Redis Hash：`crawler:stats:{spider_name}`，Pipeline 每处理 100 条 `HINCRBY` 一次，FastAPI 读 Redis → 返回；前端 10 秒轮询刷新。

### A.6 docker-compose 新增服务（阶段0 可与阶段1一起启动）

```yaml
  crawler:
    build: ./data-crawler
    container_name: medgraph-crawler
    ports:
      - "8010:8010"     # monitor FastAPI
    depends_on:
      kafka:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - CRAWLER_MODE=hybrid
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - REDIS_URL=redis://redis:6379/3
      - RUN_ON_START=true   # 容器启动自动跑一轮 hybrid 采集
    volumes:
      - ./data-crawler/output:/app/output
      - ./spark-jobs/data/sample:/app/output/linked_to_spark_sample  # ODS 直通阶段2
```

---

## 1. 阶段1 — 基础设施层（Docker Compose）

### 1.1 工程根目录 Mono Repo 结构（更新：新增 data-crawler）

```
MedGraphRAG/
├── doc/                          # 设计文档 & 本实施规格
├── docker-compose.yml            # 阶段0+1：全栈容器编排（含 crawler）
├── .env.example                  # 环境变量模板（含 CRAWLER_MODE 等）
│
├── data-crawler/                 # 阶段0：Scrapy 爬虫 + Kafka 接入 + 监控 API（见 §A）
│
├── infra/                        # 阶段1：中间件初始化脚本（按服务分目录）
│   ├── neo4j/
│   │   ├── init.cypher           #   建约束、建索引、导入 43 节点 + 100+ 边（阶段0爬虫有数据后阶段2覆盖增强）
│   │   └── constraints.md
│   ├── milvus/
│   │   └── init_collection.py    #   pymilvus 创建 clinical_embeddings collection
│   ├── redis/
│   │   ├── redis.conf            #   开启 AOF、调优内存策略
│   │   └── sliding_window.lua    #   滑动窗口限流 Lua 脚本（供 Java 端调用）
│   ├── mongodb/
│   │   └── init.js               #   创建 medgraph DB + chat_session 索引 + 爬虫指标临时集合
│   ├── hbase/
│   │   └── init-hbase.sh         #   建 medical_corpus:drug_detail 表 & 两个列族
│   └── kafka/
│       └── create-topics.sh      #   创建 medical_raw_topic（分区 3，副本 1）+ medical_etl_events topic
│
├── spark-jobs/                   # 阶段2：Spark 作业模块（见 §2；含 Python pandas 等价脚本 py_equivalents/）
├── rag-ai-service/               # 阶段3：Python FastAPI 服务（见 §3）
├── java-backend/                 # 阶段4：Spring Boot 多模块（见 §4；新增 3 个可视化指标 Controller）
├── web-frontend/                 # 阶段5：Vue 3 前端（可视化增强版，6 大主页面见 §B/§5）
└── README.md
```

### 1.2 docker-compose.yml 服务清单（更新：加 crawler 服务 + compose profiles 分组）

| 服务名 | 镜像 | 端口 | 卷挂载 | 依赖 | profiles |
|--------|------|------|--------|------|----------|
| zookeeper | confluentinc/cp-zookeeper:7.5.0 | 2181 | infra/kafka/data/zk | - | infra |
| kafka | confluentinc/cp-kafka:7.5.0 | 9092 | infra/kafka/data/kafka | zookeeper | infra |
| **crawler** | **本地构建 ./data-crawler** | **8010** | **data-crawler/output; spark-jobs/data/sample (linked)** | **kafka, redis** | **crawler, full** |
| spark-master | bitnami/spark:3.4.1 | 7077, 8080 | spark-jobs:/opt/spark-jobs | - | spark, full |
| spark-worker | bitnami/spark:3.4.1 | - | spark-jobs:/opt/spark-jobs | spark-master | spark, full |
| hbase | harisekhon/hbase:2.4 | 16000, 16010 | infra/hbase/init-hbase.sh | - | storage, full |
| neo4j | neo4j:5.12-community | 7474, 7687 | infra/neo4j/data; infra/neo4j/init.cypher | - | storage, full |
| etcd | quay.io/coreos/etcd:v3.5.5 | 2379 | infra/milvus/data/etcd | - | storage, full |
| minio | minio/minio:RELEASE.2023-03-20T20-16-18Z | 9000, 9001 | infra/milvus/data/minio | - | storage, full |
| milvus-standalone | milvusdb/milvus:v2.3.0 | 19530 | infra/milvus/data/milvus | etcd, minio | storage, full |
| attu | zilliz/attu:v2.3.0 | 3000 | - | milvus-standalone | storage, full |
| redis | redis:7.0-alpine | 6379 | infra/redis/redis.conf; infra/redis/sliding_window.lua | - | infra, full |
| mongodb | mongo:6.0 | 27017 | infra/mongodb/init.js; infra/mongodb/data | - | storage, full |
| xxl-job-admin | xuxueli/xxl-job-admin:2.4.0 | 8081 | - | mongodb | scheduler, full |
| rag-ai-service | 本地构建 rag-ai-service/Dockerfile | 8000 | - | neo4j, milvus, redis, mongodb | ai, full |
| java-backend | 本地构建 java-backend/gateway/Dockerfile | 8080 | - | rag-ai-service, redis, mongodb, xxl-job-admin, crawler(软依赖) | app, full |
| web-frontend | 本地构建 web-frontend/Dockerfile (Nginx) | 80 | - | java-backend | app, full |

> compose profiles 用法：
> - `docker compose --profile infra up`：只起 zk/kafka/redis（最省资源 3 容器，爬虫+Java+AI 本地跑）
> - `docker compose --profile storage up`：起所有存储（neo4j/milvus/hbase/mongo）
> - `docker compose --profile full up -d`：一键起全部

### 1.3 .env.example 变量清单（新增爬虫相关）

```bash
# 原有变量（略：TZ/NEO4J/MILVUS/REDIS/MONGO/OPENAI/JWT/XXL-JOB 保持不变）

# ===== 新增：爬虫配置 =====
CRAWLER_MODE=hybrid                 # real / mock / hybrid
CRAWLER_RUN_ON_START=true           # 容器启动自动跑一轮
CRAWLER_REQUEST_INTERVAL_MS=1000    # 每页间隔 1 秒
CRAWLER_MAX_RETRY=3                 # 单页最大重试
CRAWLER_DAILY_LIMIT=20000           # 单日采集上限（防爬爆）
CRAWLER_KAFKA_TOPIC=medical_raw_topic
CRAWLER_REDIS_DB=3                  # 爬虫指标存 Redis DB 3，避免和限流/缓存冲突
```

### 1.4 Neo4j init.cypher 示例数据规格（最小完备集）— 保持不变
### 1.5 Milvus clinical_embeddings Collection Schema — 保持不变
### 1.6 HBase 建表 & 示例数据 — 保持不变

---

## 2. 阶段2 — 数据层与图谱构建（Spark 作业）

### 2.1 Scala 依赖 & 构建 — 保持不变
### 2.2 示例样本数据（spark-jobs/data/sample/）— 保持不变
> 补充：阶段0 爬虫 output 已软链到这里；优先使用阶段0 的真实/合成 ODS JSONL；如果为空则使用内置 10 CSV 示例。

### 2.3 七个作业的输入输出契约 — 保持不变

**新增**：`spark-jobs/py_equivalents/` 目录提供 7 个 Pandas 版等价脚本（§6 风险降级）：
- `01_ods_to_dwd.py`、`02_neo4j_bulk_loader.py`、`03_milvus_indexer.py`、`04_hbase_bulk_loader.py`、`05_pagerank_calculator.py`、`06_ads_pipeline.py`、`07_louvain_community.py`
- 无 Spark 环境时，单命令 `cd spark-jobs/py_equivalents && python run_all.py` 就能完成整个数据流程，输出完全相同。
- 另外新增一个 Spark 作业 `ETLMonitorReporter.scala`（& Python 版）：将每个作业的开始/结束时间、处理行数、耗时、状态 `SINK` 到 Redis + MongoDB `etl_job_history` 集合 → 供前端「数仓 ETL 看板」折线/Gantt 可视化。

### 2.4 一键运行入口脚本 — 保持不变

---

## 3. 阶段3 — AI 计算中枢（Python FastAPI Graph RAG）

§3.1 ~ §3.9 全部保持不变；新增 2 个分析指标端点（供前端「问答效果分析」页消费）：

```
GET /api/v1/analysis/chat-stats?range=7d
→ {
    total_sessions, total_messages, total_tokens_used,
    avg_response_ms, avg_tokens_per_answer,
    daily_trend: [{date, sessions, messages}],          # 折线图用
    intent_distribution: [{intent, count}],             # 饼图用
    top_asked_questions: [{query, count}],              # 词云用
    avg_hop_count_per_trace: number,                    # 图谱跳数均值
    cache_hit_rate: number 0~1,                         # 二级缓存命中率
  }
```

持久化策略：rag-ai-service 每次 `done` 事件后异步写一条 `MongoDB (medgraph.analysis_chat_logs)` 文档，上述接口为预聚合 + Redis 1 分钟缓存。

---

## 4. 阶段4 — Java 后端业务调度中枢（Spring Boot 多模块）

§4.1 ~ §4.2 全部保持不变；**新增 3 个可视化指标 Controller + 1 Service**（汇总爬虫/ETL/问答三路指标，前端统一调用 Java 网关，避免前端直连 3 个后端）：

### 新增模块组件

**位置：** java-backend 合并模式下，放在 gateway 模块下新建包 `com.mo.medgraph.gateway.controller.analysis`

| 新增类 | 职责 |
|--------|------|
| `CrawlerMetricsController` | **透传** 阶段0 monitor_app.py :8010 的所有接口（WebClient 转发），路径统一加前缀 `/api/v1/crawler/*`，附 JWT 校验（爬虫监控不暴露给匿名） |
| `EtlMetricsController` | **新增指标聚合**：读 Redis `ads:*` 键 + MongoDB `etl_job_history` 集合 → 提供数仓 ETL 看板所需 6 个接口 |
| `AnalysisController` | **汇总**：问答分析 → 转发 `rag-ai-service:8000/api/v1/analysis/*` + 按日期范围参数过滤；Java 侧追加限流/QPS 指标拼接，最终输出前端「问答效果分析」5 类图表的单端点 `/api/v1/analysis/chat-full?from=&to=` |
| `MonitorAggregationService` | 公共服务：缓存爬虫/ETL/问答三路指标（10s Caffeine），避免前端高频刷新打爆底层服务 |

### EtlMetricsController 接口清单（数仓 ETL 看板用）

```
GET /api/v1/etl/layer-stats
  → {ods:{rows,tables}, dwd:{...}, ads:{...}}          → 3 层数据量玫瑰图
GET /api/v1/etl/job-history?limit=30
  → [{job_name, status, start_ts, end_ts, duration_ms, input_rows, output_rows, error_msg}]
  → Gantt 图 + 作业执行时间线
GET /api/v1/etl/page-rank-top?n=20
  → [{node_name, node_type, pagerank, community}]      → 图挖掘 Top20 PageRank 柱状图
GET /api/v1/etl/community-size
  → [{community_id, node_count, top_drug, top_disease}]→ Louvain 社区规模饼图/树图
GET /api/v1/etl/ingredient-heatmap
  → 对称 N×N 矩阵（前 20 药品）的 Jaccard 相似度 → 成分重叠热力图
GET /api/v1/etl/top-contraindications-n?n=50
  → [{pair:[a,b], level, risk_detail, case_count}]    → 禁忌频次 Top 50 柱+表联动
```

这些接口的数据来源是阶段2 `ADSPipeline.scala` 写入的 Redis ADS 宽表 + `ETLMonitorReporter.scala` 写的 MongoDB 作业历史。

### 4.2 Dashboard 指标接口扩展
原 §4.2.5 设计文档 §5.2 字段保持 **100% 向后兼容**，在 JSON 的 `data` 下新增 3 个可选字段（crawler_stats、etl_latest_status、analysis_summary），方便大屏顶栏额外显示。

---

## B. 阶段5 可视化增强 — 前端 6 大主页面完整设计

### B.1 前端路由 & 导航扩展（原 3 页 → 6 页 + 1 登录）

```typescript
// web-frontend/src/router/index.ts
const routes = [
  { path: '/login', component: Login },
  {
    path: '/', component: Layout, redirect: '/dashboard',
    children: [
      // ===== 新增 4 个可视化页面 =====
      { path: 'crawler',   component: CrawlerHubView,       meta: { title: '数据采集中枢', icon: 'Download', roles: ['ROLE_ADMIN'] } },
      { path: 'etl',       component: EtlMonitorView,       meta: { title: '数仓ETL看板', icon: 'DataAnalysis', roles: ['ROLE_ADMIN'] } },
      { path: 'graph-mining', component: GraphMiningView,   meta: { title: '图挖掘分析',  icon: 'Share', roles: ['ROLE_ADMIN','ROLE_USER'] } },
      { path: 'chat-analysis', component: ChatAnalysisView, meta: { title: '问答效果分析', icon: 'Histogram', roles: ['ROLE_ADMIN'] } },
      // ===== 原 3 页保持不变 =====
      { path: 'dashboard', component: DashboardView,        meta: { title: '宏观指标大屏', icon: 'Odometer' } },
      { path: 'graph',     component: GraphView,            meta: { title: '知识图谱拓扑', icon: 'Connection' } },
      { path: 'chat',      component: ChatWorkbench,        meta: { title: '智能问答工作台', icon: 'ChatDotRound' } },
    ],
  },
]
```

> 左侧菜单按「采集 → ETL → 图挖掘 → 问答分析 → 大屏 → 图谱 → 问答工作台」顺序排列，体现数据流全链路可视化。

---

### B.2 新增页面 1：数据采集中枢（CrawlerHubView.vue）

**目标：** 可视化阶段0爬虫的实时进度。

**布局（12 栅格）：**
```
┌──────────── col 12：KPI 卡片区（6 个） ──────────────┐
│ 今日采集量 | 累计采集量 | 采集速率/分 | Kafka Lag │
│ 活跃爬虫数 | 健康分数(0~100)                          │
├──── col 7：实时采集速率折线（双轴） ───┬── col 5：数据源饼图 ─┤
│ 近 1 小时每分钟三条曲线(csv/drug/     │ 各数据源占比环形      │
│ guideline)，Kafka Lag 红色面积叠加     │ 健康分数颜色标注      │
├──── col 7：Top 错误分布柱状 ──────────┬── col 5：Spider 表格 ┤
│ 错误原因 Top 10 频次                  │ Spider 列表(状态绿/   │
│                                       │ 黄/红开关按钮+手动触发│
├──────────── col 12：ODS 预览 Table ──────────────────┤
│ 标签页: 药品 / 疾病 / 指南，各 20 条，支持搜索和导出    │
└──────────────────────────────────────────────────────┘
```

**交互亮点：**
- 速率折线 10 秒自动刷新，新数据 append 而不是重绘（ECharts `appendData`）
- Spider 表格每行「立即执行」按钮 → `POST /api/v1/crawler/spider/:name/run` → 弹出 `ElMessage` 成功 + 折线图约 10 秒后出现尖峰
- Kafka Lag ≥ 10000 时卡片红色闪烁 + 提示「消费端未启动或积压严重」

---

### B.3 新增页面 2：数仓 ETL 看板（EtlMonitorView.vue）

**目标：** 可视化阶段2 Spark 7 个作业的执行历史 + 三层数据量 + ADS 聚合结果预览。

**布局：**
```
┌──── col 12：ODS → DWD → ADS 三层桑基图 ──────────────┐
│ 左柱 ODS 原始行数 → 中柱 DWD 清洗后行数 → 右柱 ADS    │
│ 聚合行数；线宽代表行数，hover 显示具体数值              │
├──── col 4：各层数据量玫瑰图 ──────────┬ col 8：作业甘特图┤
│ ODS/DWD/ADS 各表行数极坐标玫瑰       │ 最近 30 次作业    │
│                                      │ 横向甘特，色块=状态│
│                                      │ (绿成功/橙重试/红失│
│                                      │ 败)，横轴=时间     │
├──── col 12：作业明细表格（带筛选） ───────────────────┤
│ 作业名 | 状态 | 开始结束 | 耗时 | 输入行 | 输出行 | 错误│
│ 行点击 → 右抽屉弹出该作业完整 stdout/Spark UI link     │
└──────────────────────────────────────────────────────┘
```

**ECharts 类型：** Sankey + PolarPie + Custom Gantt + ElTable。

---

### B.4 新增页面 3：图挖掘分析（GraphMiningView.vue）

**目标：** 把阶段2 Spark GraphX 的 PageRank、Louvain 社区、成分重叠矩阵的结果**结构化可视化**（和 GraphView 的自由交互图谱不同，此页专注挖掘结果分析）。

**布局：**
```
┌──── col 6：PageRank Top 20 横向柱状 ─────┬── col 6：社区规模 旭日图 ┐
│ 按节点类型分层着色（💊🏥⚗️🤒）         │ 外=社区，内=节点类型占比  │
│ 柱长=pagerank，barLabel 显示数值         │ hover 显示社区 top 成员   │
│ 点击柱子 → 跳 GraphView 并高亮该节点     │                          │
├──── col 8：成分重叠 20×20 热力图 ────────┬── col 4：禁忌 Top50 列表 ┐
│ X/Y=Top 20 药品名                        │ 风险三色分级 + 搜索框     │
│ 颜色=Jaccard 相似度 (0=白 → 1=深红)      │ 每行: [A药↔B药] 风险级别 │
│ hover 显示具体重叠成分 + 过量建议         │  + case_count 柱状微图    │
│ 单元格点击 → 弹窗展示两药详细成分并跳转   │ 点击行 → Chat工作台自动填 │
│ Chat 工作台预填「X和Y能同服吗？」         │  充并定位到这条问答       │
└──────────────────────────────────────────────────────────────────────┘
```

**交互亮点：热力图 → Chat 工作台 一键联动**（`router.push('/chat') + pinia.chatStore.prefillQuery()`），体现挖掘结果驱动业务闭环。

---

### B.5 新增页面 4：问答效果分析（ChatAnalysisView.vue）

**目标：** 阶段3 问答 + 阶段4 Java 限流/QPS 的全链路运营效果分析。

**布局：**
```
┌──── col 12：8 KPI 卡片 ───────────────────────────────────────┐
│ 会话数 | 消息数 | 总Token | 平均响应ms | 缓存命中率% | 限流拦截 │
│ 平均图谱跳数 | 平均检索chunk数                                   │
├──── col 7：会话 & Token 7日趋势(双轴) ──┬── col 5：意图分布饼 ──┤
│ 柱=会话数，折线=Token 用量；日期选择器 │ 5 类意图占比 + 列表明细 │
├──── col 7：热门问题词云 ───────────────┬── col 5：QPS 秒级曲线 ──┤
│ wordcloud2.js，字体大小=提问次数       │ 最近 5 分钟限流 QPS &   │
│ 词云点击 → 跳 Chat 工作台自动发问      │ 实际通过 QPS 双色面积图 │
├──── col 12：最近 50 条问答明细表格 ────────────────────────────┤
│ 时间 | 用户 | Query | 意图 | 响应ms | Token | 缓存命中 | 操作(溯源│
│ 抽屉=retrieval_trace + 和 ChatWorkbench 复用 RetrievalTraceDrawer│
└────────────────────────────────────────────────────────────────┘
```

**词云技术选型：** `wordcloud2.js`（vue-wordcloud2 wrapper），中文 12px ~ 72px，禁用旋转，主题色医疗蓝。

---

### B.6 原有三页增强

原 **DashboardView、GraphView、ChatWorkbench** 功能全部保留，新增：
1. Dashboard 顶栏下方加一条 5 色「全链路健康状态条」：采集绿/ETL绿/图谱绿/AI绿/限流正常绿 → 任一异常变橙/红并加 tooltip
2. GraphView 顶部新增 Tab 切换：「拓扑交互」(原 G6) / 「挖掘分析」(直接跳 GraphMiningView)
3. ChatWorkbench 对话气泡右上角加「📊 分析」按钮：当前会话问答 → 弹 mini 分析窗（响应时延、引用了几条图谱路径/几个 chunk）

---

### 5.x 其他前端部分（§5.1 依赖/§5.3 打字效果/§5.4 溯源抽屉/§5.5 图谱联动/§5.6 图表/§5.7 Nginx）全部保持不变

**新增依赖**（package.json 额外加）：
```json
"vue-wordcloud2": "^1.1.1",
"echarts-wordcloud": "^2.1.0",
"@antv/g2plot": "^2.4.31",
"@antv/s2": "^1.52.0"       // 热力图可选项（复杂时用，简单用 ECharts heatmap 即可）
```

---

## 5. 阶段5 原始设计（保留 + 可视化增强叠加）
> （内容不变：§5.1 依赖、§5.2 路由守卫、§5.3 SSE 打字、§5.4 溯源抽屉、§5.5 Graph/Chat 联动、§5.6 Dashboard 原 8 组件、§5.7 Nginx）

---

## 6. 风险与降级策略（新增爬虫 & 可视化相关风险）

| 风险 | 触发条件 | 降级策略 |
|------|---------|---------|
| 机器内存不足 < 16GB | 全部容器同时启动 OOM | docker-compose profiles 分组启动（infra / crawler / storage / ai / app），默认只起 infra，AI 和 Java 本地跑；Java 合并单体模式省内存 |
| 无 LLM API Key | OPENAI_API_KEY 空 | 自动走 MockLLM（内置 10 问答对 + 逐字符模拟，问答分析页依然显示完整分析数据） |
| Milvus 向量模型下载失败 | 离线/无 HF 网络 | 随机 384 维向量 + warn 日志；GraphMining 页仍完整可看（不依赖向量） |
| HBase 启动异常 | Windows Docker 资源不足 | WarehouseRetriever fallback 到 MongoDB drug_detail 集合；ETL 看板 HBase 相关图表显示黄色占位，标注「HBase 不可用，已跳过」 |
| **无 Spark 集群** | 无 spark-submit 环境 | 自动走 **spark-jobs/py_equivalents/*.py（Pandas 等价脚本）**，纯 Python 跑完 7 作业，GraphMining 页数据完整 |
| XXL-Job 调度异常 | 阶段1调度服务不稳定 | 所有 Job 提供手动 HTTP 触发端点（SchedulerManualController）；ETL 看板作业列表「立即重跑」按钮直达 |
| **真实爬虫站点不可达/反爬封禁** | NMPA/CMeKG 站点封禁或返回空 | 3 种兜底：①Hybrid 模式单 Spider 连续失败 10 页自动切 generator；②Crawler 页手动触发 generator 立即生成；③Spark 作业 fallback 到示例 CSV（10 核心） |
| **前端图表空白 / 无数据** | 阶段0~3 任一步未跑，指标接口返回空数组 | 所有图表 `emptyState` 自定义：医疗蓝 SVG +「暂无数据，点击一键生成演示数据」按钮 → 前端直调 `/api/v1/etl/generate-demo` 接口，后端注入 1 个月合成运营数据，保证 6 个页面**任一时刻打开都不空** |
| Kafka 不可用 | zk/kafka 容器挂 | Crawler KafkaProducerPipeline 自动检测失败 → 100% 写本地 JSONL → Spark 作业直接读，不丢数据；Crawler 页 Kafka Lag 卡片灰色显示「Kafka 离线，已写入本地」 |

---

## 7. Spec 验收清单（更新：覆盖阶段0 + 新增可视化）

**阶段0 爬虫采集验收：**
- [ ] `docker compose --profile crawler up crawler` 容器启动无异常
- [ ] monitor FastAPI :8010 `/crawler/stats` 返回 3 个 spider 统计（real/mock/hybrid 任一模式）
- [ ] Kafka `kafka-console-consumer --topic medical_raw_topic` 能看到消息（至少 100 条）
- [ ] 前端「数据采集中枢」6 张卡片有数值，折线图 10 秒刷新有变化，手动触发按钮可用
- [ ] ODS 预览 3 个标签页（药品/疾病/指南）均有 10+ 条数据可导出 CSV

阶段1 验收 — 保持不变
阶段2 验收（新增项）：
- [ ] `py_equivalents/run_all.py` 路径也能完整跑通并产出相同 Neo4j 属性
- [ ] MongoDB `etl_job_history` 集合 ≥ 7 条文档
- [ ] 前端「数仓 ETL 看板」Sankey 图/玫瑰图/甘特图/表格均有数据

阶段3 验收（新增项）：
- [ ] `/api/v1/analysis/chat-stats` 返回 9 字段非空
- [ ] 问答 3 次 + 前端点击 3 页跳转后，`analysis_chat_logs` ≥ 3 条

阶段4 验收（新增项）：
- [ ] `/api/v1/crawler/stats`（Java 透传）200 OK
- [ ] `/api/v1/etl/layer-stats` / `/api/v1/etl/page-rank-top` / `/api/v1/etl/community-size` / `/api/v1/etl/ingredient-heatmap` / `/api/v1/etl/top-contraindications-n` 五个新接口全部 200 + 非空数组
- [ ] `/api/v1/analysis/chat-full` 200 OK

**阶段5 可视化增强验收（新增 4 页 + 原 3 页）：**
- [ ] 左侧菜单显示 6 项主菜单，菜单顺序：采集中枢 → ETL看板 → 图挖掘 → 问答分析 → 大屏 → 图谱 → 问答工作台
- [ ] CrawlerHubView 6 张卡片 + 折线 + 饼 + 柱状 + 表格 5 组件全部有渲染无空白
- [ ] EtlMonitorView Sankey + 玫瑰 + 甘特 + 表格 4 组件有数据，作业行点击弹出抽屉
- [ ] GraphMiningView PageRank 柱/社区旭日/成分热力/Top50 禁忌表 4 组件有数据；**热力图单元格 → Chat 预填跳转** 功能可用
- [ ] ChatAnalysisView 8 KPI + 双轴趋势 + 意图饼 + 词云 + QPS 面积 + 50 条表格 6 组件全部有渲染；**词云点击 → Chat 预填跳转** 可用
- [ ] Dashboard 全链路健康状态条：5 色 5 段全部绿色 + tooltip 正常
- [ ] 所有页面「暂无数据」点击后 3 秒内图表渲染出演示数据
- [ ] 登出 → 登录 → 刷新 → 全链路 6 页跳转无 404 / 无 JS Console error

原阶段5 UI & 交互验收项 — 保持不变
