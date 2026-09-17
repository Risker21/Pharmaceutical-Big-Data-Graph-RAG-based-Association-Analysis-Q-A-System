package com.mo.medgraph.etl

object ETLMonitorReporter {
  def report(jobName: String, status: String, durationMs: Long, inputRows: Long, outputRows: Long): Unit = {
    println(s"[ETL Monitor] Job: $jobName | Status: $status | Duration: ${durationMs}ms | In: $inputRows | Out: $outputRows")
  }
}
