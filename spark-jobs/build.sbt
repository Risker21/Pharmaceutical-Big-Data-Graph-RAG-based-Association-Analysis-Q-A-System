name := "MedGraphRAG-SparkJobs"
version := "1.0.0"
scalaVersion := "2.12.18"

val sparkVersion = "3.4.1"
val neo4jConnectorVersion = "5.12.0"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-graphx" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-mllib" % sparkVersion % "provided",
  "org.neo4j" %% "neo4j-connector-apache-spark_2.12" % neo4jConnectorVersion,
  "org.apache.hbase" % "hbase-client" % "2.4.16" excludeAll(
    ExclusionRule(organization = "org.slf4j")
  ),
  "org.apache.hbase.connectors.spark" % "hbase-spark" % "1.0.1",
  "redis.clients" % "jedis" % "4.4.3",
  "org.mongodb.spark" % "mongo-spark-connector_2.12" % "10.1.1",
  "org.scalatest" %% "scalatest" % "3.2.15" % Test
)

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
