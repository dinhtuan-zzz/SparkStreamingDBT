from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, StringType, DateType
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
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2")
            .enableHiveSupport()
        )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    logging.info("Spark session created successfully")
    return spark

# Spark expects schemas to be present before writing to it
schema_name = "raw"
topic_name = "dev_api_data"
delta_checkpoint_path = "/delta/checkpoints/kafka_offset"
schema_tracking_path = "/delta/checkpoints/kafka_schema"

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
            .option("schemaTrackingLocation", schema_tracking_path) \
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

    # Định nghĩa schema cho dữ liệu JSON trong cột json_valu
    df = df.selectExpr("CAST(value AS STRING) as json_value")

    json_value_schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("uid", StringType(), False),
        StructField("password", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("username", StringType(), True),
        StructField("email", StringType(), True),
        StructField("avatar", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("phone_number", StringType(), True),
        StructField("social_insurance_number", StringType(), True),
        StructField("date_of_birth", DateType(), True),
        StructField("employment", StructType([
            StructField("title", StringType(), True)
        ]), True),
        StructField("address", StructType([
            StructField("city", StringType(), True),
            StructField("street_name", StringType(), True),
            StructField("street_address", StringType(), True),
            StructField("zip_code", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            StructField("coordinate", StructType([
                StructField("lat", DoubleType(), True),
                StructField("lng", DoubleType(), True)
            ]), True),
        ]), True),
        StructField("credit_card", StructType([
            StructField("cc_number", StringType(), True)
        ]), True)
    ])

    parsed_df = df.withColumn("data", from_json(col("json_value"), json_value_schema)).select("data.*")
    
    return parsed_df

def start_streaming(parsed_df, spark):
    """
    Starts the streaming to table spark_streaming.rappel_conso in postgres
    """
    table_name = f"{schema_name}.{topic_name}"

    query = parsed_df.writeStream \
            .format("delta") \
            .option("checkpointLocation", delta_checkpoint_path) \
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




