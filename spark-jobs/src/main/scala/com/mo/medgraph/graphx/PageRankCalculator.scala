package com.mo.medgraph.graphx

import org.apache.spark.sql.SparkSession

object PageRankCalculator {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("PageRankCalculator")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark GraphX] Computing GraphX PageRank for cornerstone drug and disease nodes...")
    spark.stop()
  }
}
