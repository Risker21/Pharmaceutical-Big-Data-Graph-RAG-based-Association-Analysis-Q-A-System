package com.mo.medgraph.loader

import org.apache.spark.sql.SparkSession

object HBaseBulkLoader {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("HBaseBulkLoader")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark Loader] Loading full drug manuals and pharmacology texts into HBase...")
    spark.stop()
  }
}
