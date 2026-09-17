#!/bin/bash
set -euo pipefail
echo "[Kafka init] Creating topics..."
kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic medical_raw_topic --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server localhost:9092 --create --if-not-exists --topic medical_etl_events --partitions 2 --replication-factor 1
echo "[Kafka init] DONE"
