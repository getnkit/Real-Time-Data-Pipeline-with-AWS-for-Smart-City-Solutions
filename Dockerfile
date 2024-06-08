# When using WSL 2, Docker runs on the Linux kernel inside WSL instead of running on the Windows kernel,
# allowing it to run Linux containers directly without the need to specify the --platform=linux/amd64 flag.
# Based on the Docker Image for Apache Spark
FROM bitnami/spark:latest

# Copy the requirements.txt file to /tmp/requirements.txt in the container
COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# --no-cache-dir prevents pip from storing the cache of downloaded packages within the Docker image.
# This helps to reduce the Docker image size and ensure dependency consistency.