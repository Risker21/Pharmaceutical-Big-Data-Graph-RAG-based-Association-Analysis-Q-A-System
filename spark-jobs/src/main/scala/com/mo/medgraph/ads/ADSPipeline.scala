package com.mo.medgraph.ads

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object ADSPipeline {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("ADSPipeline")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark ADS] Running ADSPipeline...")
    val dataPath = sys.env.getOrElse("DATA_PATH", "data/sample")
    val interactionsDf = spark.read.option("header", "true").csv(s"$dataPath/drug_interaction.csv")
    val highRisk = interactionsDf.filter(col("level") === "High")
    println(s"[Spark ADS] Calculated ${highRisk.count()} high-risk contraindications for ADS layer.")
    spark.stop()
  }
}
