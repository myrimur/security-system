from time import sleep
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, sum

from glob import glob
#
# f = open("/opt/app/results/demofile2.txt", "w")
# f.write("Now the file has more content!")
# f.close()

spark = SparkSession.builder \
    .appName("Analytics") \
    .config("spark.cassandra.connection.host", "face-recognition-cassandra-node-1") \
    .getOrCreate()
print(glob('/opt/app/*'))
print(glob('/opt/app/results/*'))
print(glob('/opt/app/results/results/*'))
print(glob('/opt/app/results/results/*.json'))
while True:
    log_df = spark.read.format("org.apache.spark.sql.cassandra").options(table="by_person_id", keyspace="appearances").load()
    mapped_df = log_df.select(col("location"), col("person_id")).withColumn("appearance_count", lit(1))
    reduced_df = mapped_df.groupBy("location", "person_id").agg(sum("appearance_count").alias("total_appearances"))
    reduced_df.repartition(1).write.json("/opt/app/results", mode="overwrite")
    log_df.printSchema()
    log_df.show(truncate=False)
    reduced_df.printSchema()
    reduced_df.show(truncate=False)
    # reduced_df.repartition(1).write.option("multiLine", "true").json("/opt/app/results", mode="overwrite")
    # sleep(5 * 60)
    print(glob('/opt/app/*'))
    print(glob('/opt/app/results/*'))
    print(glob('/opt/app/results/results/*'))
    print(glob('/opt/app/results/results/*.json'))
    sleep(60)

# log_df = spark.read.format("org.apache.spark.sql.cassandra").options(table="by_person_id", keyspace="appearances").load()
# mapped_df = log_df.select(col("location"), col("person_id")).withColumn("appearance_count", lit(1))
# reduced_df = mapped_df.groupBy("location", "person_id").agg(sum("appearance_count").alias("total_appearances"))
# reduced_df.repartition(1).write.json("/opt/app/results", mode="overwrite")

# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName('SimpleSparkProject').getOrCreate()
#
# columns = ["name","languagesAtSchool","currentState"]
# data = [("James,,Smith",["Java","Scala","C++"],"CA"), \
#     ("Michael,Rose,",["Spark","Java","C++"],"NJ"), \
#     ("Robert,,Williams",["CSharp","VB"],"NV")]
#
# df = spark.createDataFrame(data=data,schema=columns)
# df.printSchema()
# df.show(truncate=False)
# df.write.json("/opt/app/results", mode="overwrite")

# from pyspark.sql import SparkSession
#
# spark = SparkSession.builder.appName('LineCounter').getOrCreate()
# df = spark.read.option("header", "true").csv('/opt/app/PS_20174392719_1491204439457_log.csv', header=True)
# print("Number of rows: ", df.count())
# df.repartition(1).write.json("/opt/app/results", mode="overwrite")
