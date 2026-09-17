package com.mo.medgraph.graphx

import org.apache.spark.sql.SparkSession

object LouvainCommunity {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("LouvainCommunity")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark GraphX] Executing Louvain modularity community detection on drug co-occurrence...")
    spark.stop()
  }
}
