from pyspark.sql import SparkSession, DataFrame
from config import configuration
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType, IntegerType


def main():
    spark = SparkSession.builder.appName("SmartCityStreaming") \
        .config("spark.jars.packages",
                # mvnrepository > Kafka 0.10+ Source For Structured Streaming > 3.5.1
                # spark can connect to kafka with this JAR file
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                # mvnrepository > Apache Hadoop Amazon Web Services Support > 3.3.1
                "org.apache.hadoop:hadoop-aws:3.3.1,"
                # mvnrepository > AWS SDK For Java > 1.11.469
                "com.amazonaws:aws-java-sdk:1.11.469") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", configuration.get('AWS_ACCESS_KEY')) \
        .config("spark.hadoop.fs.s3a.secret.key", configuration.get('AWS_SECRET_KEY')) \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()

    # When this method is called, SparkContext will only log messages with a severity level of WARN or higher (WARN, ERROR, FATAL).
    # Messages with a severity level lower than WARN (DEBUG, INFO) will not be logged.
    # This can reduce the amount of data logged to the executor consoles, potentially improving Spark's performance.
    spark.sparkContext.setLogLevel("WARN")

    # Vehicle schema
    vehicle_schema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("brand", StringType(), True),
        StructField("model", StringType(), True)
    ])

    # GPS schema
    gps_schema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("speed", DoubleType(), True),
        StructField("direction", StringType(), True),
        StructField("vehicle_type", StringType(), True)
    ])

    # Traffic schema
    traffic_schema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("camera_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("snapshot", StringType(), True)
    ])

    # Weather schema
    weather_schema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("temperature", DoubleType(), True),
        StructField("weather_condition", StringType(), True),
        StructField("precipitation", DoubleType(), True),
        StructField("wind_speed", DoubleType(), True),
        StructField("humidity", IntegerType(), True),
        StructField("air_quality_index", DoubleType(), True)
    ])

    # Emergency schema
    emergency_schema = StructType([
        StructField("id", StringType(), True),
        StructField("device_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("location", StringType(), True),
        StructField("incident_id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("snapshot", StringType(), True),
        StructField("status", StringType(), True),
        StructField("description", StringType(), True)
    ])

    # Nested functions, also known as inner functions, are functions defined within the scope of other functions.  
    # The inner functions can access the variables and parameters of the outer function
    def read_kafka_topic(topic, schema):
        return (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', 'broker:29092')
                .option('subscribe', topic)
                .option('starting_offsets', 'earliest')
                .load()
                .selectExpr('CAST(value AS STRING)')
                .select(from_json(col('value'), schema).alias('data'))
                .select('data.*')
                # Setting a watermark defines a time duration for potential delays in data arrival. \
                # This ensures that even if data arrives late within the specified window, the system can still process it.
                .withWatermark('timestamp', '2 minutes')
                )


    def stream_writer(input_parameter: DataFrame, checkpoint_folder, output):
        return (input_parameter.writeStream
                .format('parquet')
                .option('checkpointLocation', checkpoint_folder)
                .option('path', output)
                .outputMode('append')
                .start()
                )

    # Read data
    vehicle_df = read_kafka_topic('vehicle_data', vehicle_schema).alias('vehicle')
    gps_df = read_kafka_topic('gps_data', gps_schema).alias('gps')
    traffic_df = read_kafka_topic('traffic_data', traffic_schema).alias('traffic')
    weather_df = read_kafka_topic('weather_data', weather_schema).alias('weather')
    emergency_df = read_kafka_topic('emergency_data', emergency_schema).alias('emergency')

    # All of this query is run sequentially, but the results may be written to S3 concurrently, 
    # causing potential conflicts if .awaitTermination() is not specified.
    query_1 = stream_writer(vehicle_df, 's3a://smart-city-data-spark-streaming/checkpoints/vehicle_data',
                            's3a://smart-city-data-spark-streaming/data/vehicle_data')
    query_2 = stream_writer(gps_df, 's3a://smart-city-data-spark-streaming/checkpoints/gps_data',
                            's3a://smart-city-data-spark-streaming/data/gps_data')
    query_3 = stream_writer(traffic_df, 's3a://smart-city-data-spark-streaming/checkpoints/traffic_data',
                            's3a://smart-city-data-spark-streaming/data/traffic_data')
    query_4 = stream_writer(weather_df, 's3a://smart-city-data-spark-streaming/checkpoints/weather_data',
                            's3a://smart-city-data-spark-streaming/data/weather_data')
    query_5 = stream_writer(emergency_df, 's3a://smart-city-data-spark-streaming/checkpoints/emergency_data',
                            's3a://smart-city-data-spark-streaming/data/emergency_data')

    # Tell the application to wait until query_5 has completed.
    query_5.awaitTermination()

# The following conditional statement checks if the Python file is being run directly (as the main program).
# If so, the code within this block will be executed.
# This is a common practice to separate code that should only run when the file is the main program- 
# from code that defines reusable functions or classes.
if __name__ == "__main__":
    main()


"""
Don't forget we are already doing a synchronization between our local jobs directory (./jobs)-
and the Spark jobs directory (/opt/bitnami/spark/jobs). 
Therefore, we will use Docker Compose to orchestrate and submit jobs to the Spark cluster.

By using this command:
docker exec -it smartcity-spark-master-1 spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 jobs/spark-city.py
"""