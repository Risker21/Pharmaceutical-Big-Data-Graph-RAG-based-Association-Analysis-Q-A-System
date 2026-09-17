#!/usr/bin/env bash
set -euo pipefail
mkdir -p output/ods_raw
if [ "${RUN_ON_START:-false}" = "true" ]; then
  echo "[crawler] RUN_ON_START=true, starting hybrid crawl + monitor..."
  (cd medical_crawler && (scrapy crawl cmekg || true) && (scrapy crawl drug_label || true) && (scrapy crawl clinical_guideline || true)) &
fi
exec uvicorn monitor_app:app --host 0.0.0.0 --port 8010 --log-level info
