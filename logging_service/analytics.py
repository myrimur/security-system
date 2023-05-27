from time import sleep
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, sum

spark = SparkSession.builder \
    .appName("Analytics") \
    .config("spark.cassandra.connection.host", "face-recognition-cassandra-node-1") \
    .getOrCreate()

while True:
    log_df = spark.read.format("org.apache.spark.sql.cassandra").options(table="by_person_id", keyspace="appearances").load()
    mapped_df = log_df.select(col("location"), col("person_id")).withColumn("appearance_count", lit(1))
    reduced_df = mapped_df.groupBy("location", "person_id").agg(sum("appearance_count").alias("total_appearances"))
    reduced_df.repartition(1).write.json("/opt/app/results", mode="overwrite")
    sleep(60)
