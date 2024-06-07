# Smart City Realtime data
## Project Overview
This project focuses on building a real-time data streaming pipeline that spans from data ingestion to processing and storage. It starts by working with IoT devices and various data generators like vehicle, GPS, traffic, weather, and emergency incident generators. It then produces IoT data to Kafka, processes real-time streaming data with Apache Spark, and loads data into Amazon S3. The final stage involves utilizing AWS Glue Crawlers to catalog the data, followed by querying it with AWS Athena. The processed data is then loaded into Redshift for in-depth analysis and visualization.

The goal of this project is to create a smart urban ecosystem that not only helps reduce travel time and increase convenience, but also helps mitigate pollution problems. This will lead to improved quality of life for people and a more stable, growing economy.
## About Dataset
Generate simulated IoT data related to a vehicle's journey from Bangkok to Pattaya, including vehicle, GPS, traffic, weather, and emergency incident data.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/b8fc5474319ca945a8730750a89e5ad407e0f095/images/Google%20Maps.jpg)
## Data Architecture
![image]()
## Implementation
### Step 1: Set up a Virtual Environment in Python
**Using virtual environments (venv) in Python helps isolate project dependencies and prevent conflicts between projects or system packages.**

Creates a Python Virtual Environment named "ENV", isolating project dependencies from the global Python environment.
```
python -m venv ENV
```
Activates the Python Virtual Environment named "ENV", allowing you to work within that isolated environment.
```
ENV\Scripts\activate
```
Installs the specified Python packages into the current Python environment and then saves a list of all installed packages to a requirements.txt file.
```
pip install confluent_json pyspark
pip freeze > requirements.txt
```
Alternatively, packages to be installed can be directly defined in the requirements.txt file. Then, install all the Python packages listed in the requirements.txt file.
```
pip install -r requirements.txt
```
### Step 2: Create a bucket on Amazon S3
This is the bucket policy configuration for this project.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/0cfe384ec850706f0122deeb0e518d584b0562c1/images/Bucket%20policy.png)
### Step 3: Install and Configure Kafka Broker, Zookeeper, and Spark Cluster Using Docker Container
Create a Dockerfile to describe how to create, then build a Docker image
```
docker build -t custom-airflow-image:2.9.1 .
```
Configure docker-compose yaml, then run the docker-compose command to run Docker containers based on the settings described in a docker-compose.yaml file

```
docker compose up
```
Access to Spark master UI
```
http://localhost:9090/
```
### Step 4: Create and execute ```main.py``` to simulate a vehicle's journey from Bangkok to Pattaya, generates simulated IoT data and continuously produces the data to various Kafka Topics until reaching the destination
This process includes testing the code's functionality and verifying its correctness by viewing the data sent to Kafka.

Execute ```main.py```

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/execute%20main.py.png)

In the Kafka broker container:

Lists all the available Kafka topics from the broker at broker:29092.
```
Exec > kafka-topics --list --bootstrap-server broker:29092
```
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/0b30171e3932d31343167b704d7f800edf2b8814/images/List%20Kafka%20Topics.png)

Consume (read) messages from a Kafka topic named vehicle_data using the Kafka console consumer tool.
```
Exec > kafka-console-consumer --topic vehicle_data --bootstrap-server broker:29092 --from-beginning
```
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/f3603a03af519f9f3bf4397a10017404006432b7/images/kafka-console-consumer.png)
### Step 5: Create and execute ```spark-city.py``` to read IoT data from Kafka topics, convert it into DataFrames, and save it to S3 in parquet format using Spark Structured Streaming
Clear the Kafka broker to remove any residual data from the topic and submit this job to the Spark cluster.
```
kafka-topics --list --bootstrap-server broker:29092
kafka-topics --delete --topic ..._data --bootstrap-server broker:29092
```
Runs a Spark job (spark-city.py) inside a Docker container (smartcity-spark-master-1).
```
docker exec -it smartcity-spark-master-1 spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 jobs/spark-city.py
```
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/execute%20spark-city.py.png)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/0cfe384ec850706f0122deeb0e518d584b0562c1/images/Spark%20master%20Running%20App.png)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/134a1a006a5989d3bb23a296829075ce8a3a3b2f/images/SmartCityStreaming%20App.png)
### Step 6: Verify that the data files have been written correctly and completely to Amazon S3
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/ab5dd0b33aadc29dde2366a1b58089b74931c694/images/smart-city-data-spark-streaming%20bucket.jpg)

Example data in the ```data``` directory

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/1fd7b7f9c7b5df4287807d774c3620dfec544f1e/images/traffic_data%20folder.jpg)

Example data in the ```checkpoint``` directory

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/ab5dd0b33aadc29dde2366a1b58089b74931c694/images/checkpoints%20folder.jpg)

- Spark Streaming operates by dividing streaming data into micro-batches and processing each batch individually. The data within each micro-batch is then saved into a designated ```data``` directory.
- Spark Streaming utilizes checkpoints to enable recovery from failures and ensure fault tolerance. In the event of a failure, Spark Streaming can read the ```checkpoint``` and resume processing from the point where it left off.

### Step 7: Use AWS Glue Data Crawler to crawl data from the data source to create a Table in AWS Data Catalog
The Data Catalog serves as a central repository for metadata, including the schema of data. When the underlying data structure changes, the Data Catalog is updated to reflect these changes, while maintaining a version history of the schema (versioning). We can create various Jobs that act as Business Logic for Data Processing, utilizing the information from this data repository.

Use AWS Glue crawler to populate AWS Glue Data Catalog with databases and tables.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/8e587f5b7c6e0babc2e25114f1738cfd51c9af20/images/Create%20Glue%20Crawler.jpg)

Data populated into AWS Glue Data Catalog tables.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/8e587f5b7c6e0babc2e25114f1738cfd51c9af20/images/Data%20Catalog%20tables.jpg)

### [Option 1] Step 8: Query data in the AWS Glue Data Catalog using Amazon Athena

Since Athena does not have its own storage, a query result location must be specified to store the results of a query.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/Athena%20result%20location.jpg)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/Query%20by%20Athena.jpg)

### [Option 2] Step 9: Use Amazon Redshift for working with AWS Glue Data Catalog.
**Step 9.1: Load data from the AWS Glue Data Catalog into Amazon Redshift**

Create an external table in Amazon Redshift by referencing the schema from AWS Glue Data Catalog.

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/Create%20schema.jpg)

**Step 9.2: Query the loaded data using Amazon Redshift Query Editor v2**

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/16362be709a6533ca345d0749963c7509a6c985c/images/Query%20by%20Redshift.jpg)

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Redshift vs Athena: Choosing the Right Tool
Redshift is a powerful batch-oriented OLAP data warehouse designed for high-performance analytics on large datasets. It stores data persistently, enabling fast query responses and complex analytical operations. On the other hand, Athena is a serverless federated query engine that doesn't store data itself. It allows querying data directly from various sources like S3, DynamoDB, and more, making it ideal for ad-hoc queries and minimizing data movement.
