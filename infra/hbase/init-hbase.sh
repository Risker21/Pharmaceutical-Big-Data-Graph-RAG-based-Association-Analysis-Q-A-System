#!/bin/bash
set -euo pipefail
echo "[HBase init] Waiting HBase..."
sleep 5
hbase shell <<'EOF'
create_namespace 'medical_corpus'
disable 'medical_corpus:drug_detail'
drop    'medical_corpus:drug_detail'
create  'medical_corpus:drug_detail', {NAME=>'info',VERSIONS=>1},{NAME=>'manual',VERSIONS=>1}
list
EOF
echo "[HBase init] DONE"
