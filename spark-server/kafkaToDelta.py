from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, IntegerType, LongType, StringType
from delta import configure_spark_with_delta_pip
import logging


logging.basicConfig(
        level=logging.INFO, format="%(asctime)s:%(funcName)s:%(levelname)s:%(message)s"
)
# Khởi tạo SparkSession

def create_spark_session() -> SparkSession:
    builder = (
            SparkSession.builder
            .appName("PySparkWithStandaloneMetastore")
            .master("spark://spark-server:7077")
            .config("spark.sql.warehouse.dir", "file:///spark-warehouse")
            .config("spark.sql.catalogImplementation", "hive")
            .config("hive.metastore.uris", "thrift://metastore-db:9083")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.apache.spark:spark-streaming-kafka-0-10-assembly_2.12-3.3.2,org.apache.spark:kafka-clients-3.4.0,org.apache.spark:commons-pool2-2.11.1,io.delta:delta-spark_2.12:3.1.0")
            .enableHiveSupport()
        )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    logging.info("Spark session created successfully")
    return spark

# Spark expects schemas to be present before writing to it
schema_name = "raw"
topic_name = "dev_api_data"
checkpoint_path = "/delta/checkpoints/daily_stream"


def create_inital_dataframe(spark):
    """
    Reads the streaming data and creates the initial dataframe accordingly.
    """

    try:

        spark.sql(f"CREATE DATABASE IF NOT EXISTS {schema_name}")

        # Đọc dữ liệu stream từ Kafka topic "daily"
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka-server:9092") \
            .option("schemaTrackingLocation", checkpoint_path) \
            .option("subscribe", f"{topic_name}") \
            .option("startingOffsets", "earliest") \
            .load()
        logging.info("Initial dataframe created successfully")
    except Exception as e:
        logging.warning(f"Initial data couldn't be create due to exception : {e}")
        raise

    return kafka_df


def create_final_dataframe(df):
    """
    Modifies the initial dataframe, and creates the final dataframe.
    """

    # Định nghĩa schema cho dữ liệu JSON trong cột json_value
    json_value_schema = StructType([
        StructField(field_name, data_type, True) for field_name, data_type in df.dtypes
    ])

    df = df.selectExpr("CAST(value AS STRING) as json_value")

    parsed_df = df.withColumn("data", from_json(col("json_value"), json_value_schema)).select("data.*")
    
    return parsed_df

def start_streaming(parsed_df, spark):
    """
    Starts the streaming to table spark_streaming.rappel_conso in postgres
    """
    table_name = f"{schema_name}.{topic_name}"

    query = parsed_df.writeStream \
            .format("delta") \
            .option("checkpointLocation", checkpoint_path) \
            .outputMode("append") \
            .toTable(table_name)
    return query.awaitTermination()

def write_to_delta():
    spark = create_spark_session()
    df = create_inital_dataframe(spark)
    df_final = create_final_dataframe(df)
    start_streaming(df_final, spark=spark)


if __name__=="__main__":
    write_to_delta()




