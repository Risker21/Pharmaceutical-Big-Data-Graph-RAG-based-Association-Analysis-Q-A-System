# 医药大数据 Graph RAG 关联分析问答系统 (MedGraphRAG)

[![Vue 3](https://img.shields.io/badge/Vue-3.4-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.2-6DB33F.svg)](https://spring.io/projects/spring-boot)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.12-blue.svg)](https://neo4j.com/)
[![Milvus](https://img.shields.io/badge/Milvus-2.3-00A1EA.svg)](https://milvus.io/)

本系统结合**多模态大数据计算引擎**与 **Graph RAG（知识图谱增强生成）**，实现海量医药异构数据治理、图谱拓扑挖掘、三路混合召回与流式智能问答，配备 7 大全链路可视化分析工作台。

---

## 🏗️ 整体架构

```
┌────────────────────────────────────────────────────────────────────────┐
│                        前端展现层 (Vue 3 + Element Plus)                │
│  [数据采集中枢] [数仓ETL看板] [图挖掘分析] [问答效果分析] [宏观指标大屏] [图谱拓扑] [问答工作台] │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP / SSE 流式长连接
┌────────────────────────────────────▼───────────────────────────────────┐
│                  Java 后端业务中枢 (Spring Boot 3.2 多模块)             │
│  - Gateway 网关 / JWT 鉴权 / RBAC / Redis Lua 滑动窗口限流 / Caffeine 二级缓存  │
│  - SSE 事件流中继 (trace / token / done) / XXL-Job 调度 / 爬虫+ETL+问答指标聚合  │
│  - service-admin (用户权限) / service-chat (会话持久化) / scheduler (调度中枢) │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ gRPC / HTTP
┌────────────────────────────────────▼───────────────────────────────────┐
│                 AI 与 Graph RAG 计算引擎 (Python FastAPI)               │
│  - 医学 NER 实体抽取与意图识别 / 向量检索 (Milvus) / 图谱多跳遍历 (Neo4j)      │
│  - 数仓规则核验 (HBase/Mongo) / Rerank 重排 / Prompt 组装 / 流式推理 (LLM/Mock) │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────────────┐
│                 离线计算与存储矩阵 (Spark + Neo4j + Milvus + Redis + Mongo)│
│  - Spark SQL / Pandas ETL (ODS→DWD→ADS) / Spark GraphX (PageRank & Louvain)│
│  - Neo4j 知识图谱 / Milvus 向量库 / Redis 缓存与限流 / MongoDB 会话与日志       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
MedGraphRAG/
├── data-crawler/            # 阶段0：Scrapy 爬虫、药理数据生成器与采集监控 API (:8010)
├── infra/                   # 阶段1：Neo4j、Redis、Mongo、Milvus、HBase、Kafka 初始化脚本
├── docker-compose.yml       # 阶段1：18 服务容器化编排 (支持 profiles)
├── spark-jobs/              # 阶段2：Spark Scala / Python 等价数仓处理与 GraphX 挖掘作业
│   ├── py_equivalents/      #   7 个免 Spark 环境的 Pandas/Python 全量等价脚本
│   └── data/sample/         #   核心药品/疾病/指南/相互作用样本库
├── rag-ai-service/          # 阶段3：Python FastAPI Graph RAG 计算引擎 (:8000)
├── java-backend/            # 阶段4：Spring Boot 3.2 多模块工程与网关 (:8080)
├── web-frontend/            # 阶段5：Vue 3 + Element Plus + ECharts + AntV G6 7 大工作台 (:5173)
├── 设计文档.md              # 核心架构设计文档
└── doc/                     # 实施方案与规格文档
```

---

## 🚀 快速启动指南

### 方式一：独立模块本地开发启动

#### 1. 启动 RAG AI 计算引擎
```bash
cd rag-ai-service
python app/main.py
```
服务将在 `http://localhost:8000` 启动，提供 SSE 流式问答与分析接口。

#### 2. 运行数仓 ETL 与图挖掘流水线
```bash
cd spark-jobs/py_equivalents
python run_all.py
```
将依次执行 ODS 清洗、图谱装载、向量索引、PageRank 重要度计算、ADS 宽表聚合与 Louvain 社区聚类。

#### 3. 启动数据采集监控服务
```bash
cd data-crawler
python monitor_app.py
```
服务将在 `http://localhost:8010` 启动。

#### 4. 启动前端可视化工作台
```bash
cd web-frontend
npm install
npm run dev
```
浏览器打开 `http://localhost:5173`。默认预置管理员账号 `admin` / `admin123` 与普通医师账号 `user` / `user123`，支持一键快捷填充登录。

---

### 方式二：Docker Compose 容器化部署

系统内置了标准的多 Profile 编排配置与一键启停脚本，支持根据服务器硬件资源弹性启动对应层级的服务。

#### 1. 确保 Docker 启动
确保本机已打开 **Docker Desktop**（Windows / Mac）或 `systemctl start docker`（Linux）。

#### 2. 一键脚本启动（Windows 用户推荐）
双击根目录下的 `docker-start.bat`，可交互式选择启动模式：
- **选项 [1] 全量模式 (Profile: full)**：启动全部 18 个服务（包含 Spark 集群、Milvus、Neo4j、Kafka、HBase、Java 网关、Vue 前端、RAG AI 等，建议 16GB+ 内存）。
- **选项 [2] 中间件模式 (Profile: infra,storage)**：仅启动 Neo4j、Milvus、Redis、MongoDB、Kafka 等存储中间件。
- **选项 [3] 核心应用模式 (Profile: app,ai)**：启动 Java 后端网关、Vue 前端与 Python Graph RAG AI 服务。
- **选项 [4] 精简核心服务**：启动 Redis + MongoDB + Neo4j + RAG AI + Java + Web。

停止服务时可直接双击 `docker-stop.bat`。

#### 3. 命令行指令参考
```bash
# 查看所有编排服务状态
docker compose ps

# 启动基础存储层 (Neo4j, Milvus, Mongo, Redis, HBase)
docker compose --profile infra --profile storage up -d

# 构建并启动全部应用与微服务
docker compose --profile full up -d --build

# 停止并清理全量容器
docker compose --profile full down
```

#### 4. 容器化服务端口与控制台清单
| 服务组件 | 容器内/宿主机端口 | 访问地址 / 认证方式 | 功能说明 |
| :--- | :--- | :--- | :--- |
| **Web 前端** | `80` | `http://localhost` | Vue 3 + Element Plus 7 大全链路可视化工作台 |
| **Java 网关** | `8080` | `http://localhost:8080` | Spring Boot 3.2 业务中枢与流式网关 |
| **RAG AI 引擎**| `8000` | `http://localhost:8000/docs` | FastAPI Graph RAG 混合检索与推理引擎 |
| **数据采集监控**| `8010` | `http://localhost:8010/docs` | Scrapy 药理数据采集中枢与状态监控 |
| **Neo4j 知识图谱**| `7474` / `7687` | `http://localhost:7474` (`neo4j` / `MedGraph123!`) | 医药图谱图数据库可视化控制台 |
| **Milvus 向量库**| `19530` / `3000` | `http://localhost:3000` (Attu 控制台) | 临床指南向量相似度检索与管理 |
| **XXL-Job 调度中心**| `8081` | `http://localhost:8081/xxl-job-admin` (`admin` / `123456`) | 分布式定时作业与离线 ETL 调度中枢 |
| **Spark Master** | `8089` | `http://localhost:8089` | Spark 3.4.1 分布式集群 Master Web UI |
| **Redis 缓存** | `6379` | `localhost:6379` | 限流与热点缓存中间件 |
| **MongoDB 库** | `27017` | `localhost:27017` (`medgraph` / `MedGraph123!`) | 问答日志与离线 ETL 历史存储 |
| **MinIO 对象存储** | `9101` | `http://localhost:9101` (`minioadmin` / `minioadmin`) | 向量存储底层 S3 控制台 |

---

## 🖥️ 前端 7 大主页面特性

1. **数据采集中枢** (`/crawler`)：实时吞吐折线、数据源健康度占比、爬虫调度控制台、ODS 原始数据即时预览与导出。
2. **数仓 ETL 看板** (`/etl`)：ODS→DWD→ADS 三层数据流动桑基图、分层数据玫瑰图、Spark 离线作业甘特历史。
3. **图挖掘分析** (`/graph-mining`)：GraphX PageRank 核心节点权重、Louvain 社群旭日图、15×15 成分重叠 Jaccard 矩阵、高危配伍禁忌 Top50 联动（**点击直接在问答工作台发起核验**）。
4. **问答效果分析** (`/chat-analysis`)：8 大运营 KPI、7 日双轴趋势、用户意图分布、热门提问词云（**点击词云自动发问**）、QPS 限流双色面积图。
5. **宏观指标大屏** (`/dashboard`)：实体与关系总数、禁忌案例排行、科室疾病分布雷达图。
6. **知识图谱拓扑** (`/graph`)：AntV G6 力导向图、节点高亮、关系筛选与搜索。
7. **智能问答工作台** (`/chat`)：多会话历史、打字机流式输出、知识图谱推导路径点亮与溯源抽屉。
