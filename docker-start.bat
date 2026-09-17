@echo off
chcp 65001 > nul
echo ========================================================
echo     MedGraphRAG 医药大数据知识图谱问答系统 - Docker 启动
echo ========================================================

echo 检查 Docker 运行状态...
docker info > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Docker Desktop 尚未启动，请先打开 Docker Desktop 客户端并等待启动就绪后再运行此脚本。
    pause
    exit /b 1
)

echo.
echo 请选择启动模式:
echo [1] 全量模式 (Profile: full - 启动全部 18 个微服务与存储组件，推荐 16GB+ 内存)
echo [2] 存储与基础组件模式 (Profile: infra,storage - 仅启动 Neo4j, Milvus, Redis, MongoDB, Kafka, HBase)
echo [3] 应用与AI服务模式 (Profile: app,ai - 启动 Java 网关, Vue 前端, Python Graph RAG AI 服务)
echo [4] 仅核心存储 (Neo4j + Redis + MongoDB + RAG AI 服务)
echo.
set /p choice="请输入选项编号 (默认为 1): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo 正在启动全量容器集群...
    docker compose --profile full up -d --build
) else if "%choice%"=="2" (
    echo 正在启动存储与基础中间件...
    docker compose --profile infra --profile storage up -d
) else if "%choice%"=="3" (
    echo 正在启动应用与AI服务...
    docker compose --profile app --profile ai up -d --build
) else if "%choice%"=="4" (
    echo 正在启动精简核心服务...
    docker compose up -d redis mongodb neo4j rag-ai-service java-backend web-frontend
) else (
    echo 未知选项，默认启动全量服务...
    docker compose --profile full up -d --build
)

echo.
echo ========================================================
echo 集群启动完成！服务访问入口:
echo   - Vue 3 前端应用:       http://localhost (或 http://localhost:5173)
echo   - Java SpringBoot 网关: http://localhost:8080/api/dashboard/overview
echo   - Python Graph RAG API: http://localhost:8000/docs
echo   - 爬虫与数据接入监控:    http://localhost:8010/docs
echo   - Neo4j 图数据库控制台:  http://localhost:7474 (neo4j / MedGraph123!)
echo   - Milvus 向量库控制台:   http://localhost:3000 (Attu)
echo   - XXL-Job 调度中心:      http://localhost:8081/xxl-job-admin (admin / 123456)
echo   - Spark Master Web UI:   http://localhost:8089
echo   - MinIO 对象存储控制台:  http://localhost:9101 (minioadmin / minioadmin)
echo ========================================================
pause
