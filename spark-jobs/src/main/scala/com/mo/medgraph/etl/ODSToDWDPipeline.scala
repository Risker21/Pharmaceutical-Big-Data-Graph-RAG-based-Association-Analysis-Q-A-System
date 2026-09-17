package com.mo.medgraph.etl

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object ODSToDWDPipeline {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("ODSToDWDPipeline")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark ETL] Running ODSToDWDPipeline...")
    val dataPath = sys.env.getOrElse("DATA_PATH", "data/sample")
    val drugsDf = spark.read.option("header", "true").csv(s"$dataPath/drugs.csv")
    val diseasesDf = spark.read.option("header", "true").csv(s"$dataPath/diseases.csv")

    println(s"[Spark ETL] Processed ${drugsDf.count()} drugs and ${diseasesDf.count()} diseases into DWD layer.")
    spark.stop()
  }
}
