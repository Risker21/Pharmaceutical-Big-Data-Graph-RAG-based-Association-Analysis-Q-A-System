#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPARK_MASTER="${SPARK_MASTER:-local[*]}"
PY_EQUIV_DIR="$SCRIPT_DIR/py_equivalents"

echo "======================================"
echo "MedGraphRAG Stage-2 Spark Jobs Runner"
echo "Mode: ${1:-spark}"
echo "======================================"

if [[ "${1:-}" == "--py" || "${1:-}" == "--pandas" || ! -x "$(command -v spark-submit 2>/dev/null)" ]]; then
  echo "[INFO] Spark not found or --py flag set → Fallback to Pandas Equivalent Scripts"
  echo "[INFO] Running: $PY_EQUIV_DIR/run_all.py ${2:-}"
  exec python3 "$PY_EQUIV_DIR/run_all.py" "${2:-}"
  exit $?
fi

echo "[INFO] Using Spark submit master=$SPARK_MASTER"
JAR_DIR="$SCRIPT_DIR/target/scala-2.12/*.jar"
if compgen -G "$JAR_DIR" > /dev/null 2>&1; then
  JAR=$(compgen -G "$JAR_DIR" | head -n 1)
  echo "[INFO] Found assembly jar: $JAR"
else
  echo "[WARN] No assembly jar found. Build with: sbt assembly"
  echo "[INFO] Falling back to Pandas equivalents (no Spark jar)"
  exec python3 "$PY_EQUIV_DIR/run_all.py" "${1:-}"
  exit $?
fi

JOBS=(
  "com.mo.medgraph.etl.ODSToDWDPipeline"
  "com.mo.medgraph.loader.Neo4jBulkLoader"
  "com.mo.medgraph.loader.MilvusIndexer"
  "com.mo.medgraph.loader.HBaseBulkLoader"
  "com.mo.medgraph.graphx.PageRankCalculator"
  "com.mo.medgraph.ads.ADSPipeline"
  "com.mo.medgraph.graphx.LouvainCommunity"
  "com.mo.medgraph.etl.ETLMonitorReporter"
)

for job in "${JOBS[@]}"; do
  echo "------ Running: $job ------"
  time spark-submit --class "$job" --master "$SPARK_MASTER" "$JAR" || {
    echo "[ERROR] Job failed: $job"
    exit 1
  }
done

echo "[OK] All 8 Spark jobs finished successfully."
