@echo off
chcp 65001 > nul
echo ========================================================
echo     MedGraphRAG 医药大数据系统 - Docker 停止与清理
echo ========================================================
echo 正在停止并移除所有容器...
docker compose --profile full down
echo 服务已全部安全停止。
pause
