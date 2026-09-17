package com.mo.medgraph.loader

import org.apache.spark.sql.SparkSession

object Neo4jBulkLoader {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Neo4jBulkLoader")
      .master(sys.env.getOrElse("SPARK_MASTER_URL", "local[*]"))
      .getOrCreate()

    println("[Spark Loader] Bulk loading entities and relationships to Neo4j graph schema...")
    spark.stop()
  }
}
