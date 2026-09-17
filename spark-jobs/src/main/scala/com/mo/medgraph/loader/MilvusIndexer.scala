package com.mo.medgraph.loader

import org.apache.spark.sql.SparkSession

object MilvusIndexer {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("MilvusIndexer")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark Loader] Indexing clinical guideline chunks into Milvus vector store...")
    spark.stop()
  }
}
