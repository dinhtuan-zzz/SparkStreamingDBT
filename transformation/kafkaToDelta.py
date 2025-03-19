from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, regexp_extract
from pyspark.sql.types import StructType, StructField, IntegerType, LongType, StringType
from delta import configure_spark_with_delta_pip

# Khởi tạo SparkSession
#builder = (
#    SparkSession.builder
#    .appName("PySparkWithStandaloneMetastore")
#    .master("spark://spark-server:7077")
#    .config("spark.sql.warehouse.dir", "file:///spark-warehouse")
#    .config("spark.sql.catalogImplementation", "hive")
#    .config("hive.metastore.uris", "thrift://metastore-db:9083")
#    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
#    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
#    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4,io.delta:delta-core_2.12:2.4.0")
#    .enableHiveSupport()
#)

#spark = configure_spark_with_delta_pip(builder).getOrCreate()

spark = SparkSession.builder \
    .appName("PySparkWithStandaloneMetastore") \
    .master("spark://spark-server:7077")  \
    .config("spark.sql.warehouse.dir", "file:///spark-warehouse") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("hive.metastore.uris", "thrift://metastore-db:9083") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,io.delta:delta-core_2.12:2.2.0") \
    .enableHiveSupport() \
    .getOrCreate()

schema_name = "raw"
topic_name = "daily"
checkpoint_path = "/delta/checkpoints/daily_stream"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema_name}")

# Định nghĩa schema cho dữ liệu JSON với các tên cột gốc (không sửa đổi ở đây)
json_value_schema = StructType([
    StructField("Pos", IntegerType(), True),
    StructField("Pos+", StringType(), True),
    StructField("Artist and Title", StringType(), True),
    StructField("Days", IntegerType(), True),
    StructField("Peak", IntegerType(), True),
    StructField("Pts", IntegerType(), True),
    StructField("Pts+", LongType(), True),
    StructField("TPts", LongType(), True),
    StructField("US", IntegerType(), True),
    StructField("UK", IntegerType(), True),
    StructField("AU", IntegerType(), True),
    StructField("AT", IntegerType(), True),
    StructField("BE", IntegerType(), True),
    StructField("CA", IntegerType(), True),
    StructField("DK", IntegerType(), True),
    StructField("FI", IntegerType(), True),
    StructField("FR", IntegerType(), True),
    StructField("DE", IntegerType(), True),
    StructField("GR", IntegerType(), True),
    StructField("IE", IntegerType(), True),
    StructField("IT", IntegerType(), True),
    StructField("JP", IntegerType(), True),
    StructField("LU", IntegerType(), True),
    StructField("MX", IntegerType(), True),
    StructField("NL", IntegerType(), True),
    StructField("NZ", IntegerType(), True),
    StructField("NO", IntegerType(), True),
    StructField("PT", IntegerType(), True),
    StructField("ES", IntegerType(), True),
    StructField("SE", IntegerType(), True),
    StructField("CH", IntegerType(), True)

])

try:
    # Đọc dữ liệu từ Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-server:9092") \
        .option("schemaTrackingLocation", checkpoint_path) \
        .option("subscribe", f"{topic_name}") \
        .option("startingOffsets", "earliest") \
        .load()

    # Chuyển đổi key và value từ binary sang string và parse JSON
    df = kafka_df.selectExpr("CAST(key AS STRING) as key", "CAST(value AS STRING) as json_value")
    parsed_df = df.withColumn("data", from_json(col("json_value"), json_value_schema)).select("key", "data.*")

    # Sửa tên các cột không hợp lệ
    parsed_df = parsed_df \
        .withColumnRenamed("Artist and Title", "artist_and_title") \
        .withColumn("Peak", regexp_extract(col("Peak"), r"^(\d+)", 1))

    table_name = f"{schema_name}.{topic_name}"

    query = parsed_df.writeStream \
            .format("delta") \
            .option("checkpointLocation", checkpoint_path) \
            .outputMode("append") \
            .toTable('raw.daily')
    query.awaitTermination()

    print(f"{table_name} table created in delta lake!")

except Exception as e:
    print(e)

