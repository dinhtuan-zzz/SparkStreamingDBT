from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, IntegerType, LongType, StringType
from delta import configure_spark_with_delta_pip


# Khởi tạo SparkSession
builder = (
        SparkSession.builder
        .appName("PySparkWithStandaloneMetastore")
        .master("spark://spark-server:7077")
        .config("spark.sql.warehouse.dir", "file:///spark-warehouse")
        .config("spark.sql.catalogImplementation", "hive")
        .config("hive.metastore.uris", "thrift://metastore-db:9083")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4,org.apache.spark:spark-streaming-kafka-0-10-assembly_2.12-3.5.4,org.apache.spark:kafka-clients-3.4.0,org.apache.spark:commons-pool2-2.11.1,io.delta:delta-spark_2.12:3.1.0")
        .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
        .config("spark.hadoop.fs.file.impl.disable.cache", "true")
        .enableHiveSupport()
    )

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Spark expects schemas to be present before writing to it
schema_name = "raw"
topic_name = "daily"
checkpoint_path = "/delta/checkpoints/daily_stream"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema_name}")

try:

    # Đọc dữ liệu stream từ Kafka topic "daily"
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-server:9092") \
        .option("schemaTrackingLocation", checkpoint_path) \
        .option("subscribe", f"{topic_name}") \
        .option("startingOffsets", "earliest") \
        .load()

    # Chuyển đổi key và value từ binary sang string
    df = kafka_df.selectExpr("CAST(key AS STRING) as key", "CAST(value AS STRING) as json_value")

    # Định nghĩa schema cho dữ liệu JSON trong cột json_value
    json_value_schema = StructType([
        StructField("Pos", IntegerType(), True),
        StructField("Pos+", StringType(), True),
        StructField("Artist and Title", StringType(), True),
        StructField("Days", IntegerType(), True),
        StructField("Peak", IntegerType(), True),
        StructField("Pts", IntegerType(), True),
        StructField("Pts+", LongType(), True),
        StructField("TPts", LongType(), True),
        StructField("US", LongType(), True),
        StructField("UK", LongType(), True),
        StructField("AU", LongType(), True),
        StructField("AT", LongType(), True),
        StructField("BE", LongType(), True),
        StructField("CA", LongType(), True),
        StructField("DK", LongType(), True),
        StructField("FI", LongType(), True),
        StructField("FR", LongType(), True),
        StructField("DE", LongType(), True),
        StructField("GR", LongType(), True),
        StructField("IE", LongType(), True),
        StructField("IT", LongType(), True),
        StructField("JP", LongType(), True),
        StructField("LU", LongType(), True),
        StructField("MX", LongType(), True),
        StructField("NL", LongType(), True),
        StructField("NZ", LongType(), True),
        StructField("NO", LongType(), True),
        StructField("PT", LongType(), True),
        StructField("ES", LongType(), True),
        StructField("SE", LongType(), True),
        StructField("CH", LongType(), True)
    ])

    # Parse dữ liệu JSON theo schema đã định nghĩa
    parsed_df = df.withColumn("data", from_json(col("json_value"), json_value_schema)).select("key", "data.*")
    
    # Sửa tên các cột không hợp lệ
    parsed_df = parsed_df \
        .withColumnRenamed("Artist and Title", "artist_and_title")

    table_name = f"{schema_name}.{topic_name}"

    query = parsed_df.writeStream \
            .format("delta") \
            .option("checkpointLocation", checkpoint_path) \
            .outputMode("append") \
            .toTable(table_name)
    query.awaitTermination()

    print(f"{table_name} table created in delta lake!")

except Exception as e:
    print(e)




