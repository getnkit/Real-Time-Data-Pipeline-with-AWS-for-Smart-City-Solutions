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
### Step 3: Install and Configure Kafka Broker, Zookeeper, and Spark Using Docker Container
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
Including testing whether the code is working correctly by viewing the data that has been sent to Kafka
at broker container: 
Exec > kafka-topics --list --bootstrap-server broker:29092 > show "... data"
Exec > kafka-console-consumer --topic vehicle_data --bootstrap-server broker:29092 --from-beginning
### Step 5: Create and execute ```spark-city.py``` to read IoT data from Kafka topics, convert it into DataFrames, and save it to S3 in parquet format using Spark Structured Streaming
Clear the Kafka broker to remove any residual data from the topic and submit this job to the Spark cluster
to remove:
kafka-topics --list --bootstrap-server broker:29092
kafka-topics --delete --topic ..._data --bootstrap-server broker:29092
docker exec -it smartcity-spark-master-1 spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.11.469 jobs/spark-city.py
### Step 6: Verify if the data files have been correctly and completely written to Amazon S3

