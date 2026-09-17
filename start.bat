@echo off
chcp 65001 >nul
echo ===================================================
echo   MedGraphRAG 医药大数据智能问答系统 一键启动器
echo ===================================================
echo [1] 启动 Python Graph RAG AI 计算引擎 (端口 8000)
echo [2] 启动 Python 数据采集监控服务 (端口 8010)
echo [3] 运行 Spark/Python 数仓与图挖掘全流水线
echo [4] 启动 Web 前端可视化工作台 (端口 5173)
echo [5] 一键启动全部服务 (开发模式)
echo ===================================================
set /p choice="请输入选项编号 (1-5): "

if "%choice%"=="1" (
    echo 正在启动 RAG AI 服务...
    cd rag-ai-service
    python app/main.py
)
if "%choice%"=="2" (
    echo 正在启动数据采集监控服务...
    cd data-crawler
    python monitor_app.py
)
if "%choice%"=="3" (
    echo 正在执行数仓与图挖掘计算流水线...
    cd spark-jobs/py_equivalents
    python run_all.py
    pause
)
if "%choice%"=="4" (
    echo 正在启动 Web 前端开发服务器...
    cd web-frontend
    npm run dev
)
if "%choice%"=="5" (
    echo 正在一键启动所有服务...
    start cmd /k "title RAG AI Service && cd rag-ai-service && python app/main.py"
    start cmd /k "title Crawler Monitor && cd data-crawler && python monitor_app.py"
    start cmd /k "title Web Frontend && cd web-frontend && npm run dev"
    echo 所有服务已在独立窗口中启动！
)
