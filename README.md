# Smart City Realtime data
## Project Overview
This project focuses on building a real-time data streaming pipeline that spans from data ingestion to processing and storage. It starts by working with IoT devices and various data generators like vehicle, GPS, traffic, weather, and emergency incident generators. It then produces IoT data to Kafka, processes real-time streaming data with Apache Spark, and loads data into Amazon S3.
## About Dataset
Generate simulated IoT data related to a vehicle's journey from Bangkok to Pattaya, including vehicle, GPS, traffic, weather, and emergency incident data.
## Architecture
![image]()
## Implementation
### Step 1: Set up a Virtual Environment in Python
**Using virtual environments (venv) in Python helps isolate project dependencies and prevent conflicts between projects or system packages.**

Creates a Python Virtual Environment named "ENV", isolating project dependencies from the global Python environment.
```bash
python -m venv ENV
```
Activates the Python Virtual Environment named "ENV", allowing you to work within that isolated environment.
```bash
ENV\Scripts\activate
```
Installs the specified Python package in the current Python environment.
```bash
pip install <python_package_name>
```
Installs all the Python packages listed in the "requirements.txt" file.
```bash
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
This process includes testing the code's functionality and verifying its correctness by viewing the data sent to Kafka. \
In the Kafka broker container: \
Lists all the available Kafka topics from the broker at broker:29092.
```
Exec > kafka-topics --list --bootstrap-server broker:29092
```
![image]()
Consume (read) messages from a Kafka topic named vehicle_data using the Kafka console consumer tool.
```
Exec > kafka-console-consumer --topic vehicle_data --bootstrap-server broker:29092 --from-beginning
```
![image]()
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
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/0cfe384ec850706f0122deeb0e518d584b0562c1/images/Spark%20master%20Running%20App.png)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/0cfe384ec850706f0122deeb0e518d584b0562c1/images/SmartCityStreaming%20App.png)
### Step 6: Verify that the data files have been written correctly and completely to Amazon S3
![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/ab5dd0b33aadc29dde2366a1b58089b74931c694/images/smart-city-data-spark-streaming%20bucket.jpg)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/1fd7b7f9c7b5df4287807d774c3620dfec544f1e/images/traffic_data%20folder.jpg)

![image](https://github.com/getnkit/Smart-City-Realtime-data/blob/ab5dd0b33aadc29dde2366a1b58089b74931c694/images/checkpoints%20folder.jpg)

