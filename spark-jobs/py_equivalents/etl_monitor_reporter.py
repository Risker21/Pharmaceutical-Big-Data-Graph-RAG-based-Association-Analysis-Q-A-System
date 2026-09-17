# -*- coding: utf-8 -*-
import time
from loguru import logger

def record_job_history(job_name, status, start_ts, end_ts, input_rows=0, output_rows=0, error_msg=""):
    duration_ms = int((end_ts - start_ts) * 1000)
    logger.info(f"[ETL Monitor] Job: {job_name} | Status: {status} | Duration: {duration_ms}ms | Input: {input_rows} | Output: {output_rows}")
