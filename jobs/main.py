# Importing pre-defined libraries
import json
import os
import random
import uuid
from datetime import datetime, timedelta
import time
from confluent_kafka import SerializingProducer

# Journey starts from Bangkok
BANGKOK_COORDINATES = {"latitude": 13.7367, "longitude": 100.5232}
# Journey ends in Pattaya
PATTAYA_COORDINATES = {"latitude": 12.9276, "longitude": 100.8771}

# Calculate movement increments
LATITUDE_INCREMENT = (PATTAYA_COORDINATES['latitude'] - BANGKOK_COORDINATES['latitude']) / 100
LONGITUDE_INCREMENT = (PATTAYA_COORDINATES['longitude'] - BANGKOK_COORDINATES['longitude']) / 100

# Environment variables for configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')  # bootstrap.servers = host:port
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')                        # os.getenv(key, default_key) If the key is not found,
GPS_TOPIC = os.getenv('GPS_TOPIC', 'gps_data')                                    # it will return the default_key value that we specified.
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_data')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC', 'emergency_data')

# Makes the output of a program that uses randomization reproducible.
# When 'random.seed(42)' is run, every subsequent call to a function in the random module (like random.randint())-
# will produce the same result within that program execution. This makes it easier to test and debug the program.
random.seed(42)

# Current time
start_time = datetime.now()
# Using .copy() is important to prevent start_location and BANGKOK_COORDINATES from referring to the same location in memory.
# Even though the value of start_location changes continuously, BANGKOK_COORDINATES remains constant and unchanged.
start_location = BANGKOK_COORDINATES.copy()


def get_next_time():
    # A variable that is declared as a global variable, if its value is modified within a function, 
    # it will also affect the same variable outside the function.
    global start_time
    start_time = start_time + timedelta(seconds=random.randint(30, 60))

    return start_time


def simulate_vehicle_movement():
    global start_location

    # Move towards Pattaya (Southeast)
    start_location['latitude'] += LATITUDE_INCREMENT  # x += y has the same meaning as x = x + y
    start_location['longitude'] += LONGITUDE_INCREMENT

    # Adding randomness to simulate actual road travel
    start_location['latitude'] += random.uniform(-0.0005, 0.0005)
    start_location['longitude'] += random.uniform(-0.0005, 0.0005)

    return start_location


def generate_vehicle_data(device_id):
    # The updated 'start_location' variable from the simulate_vehicle_movement() function is stored in the 'location' variable
    location = simulate_vehicle_movement()
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': get_next_time().isoformat(),
        'location': (location['latitude'], location['longitude']),
        'speed': random.uniform(10, 80),
        'direction': 'Southeast',
        'brand': 'HONDA',
        'model': 'CR-V',
    }


def generate_gps_data(device_id, timestamp, vehicle_type='private'):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': timestamp,
        'speed': random.uniform(10, 80),
        'direction': 'Southeast',
        'vehicle_type': vehicle_type
    }


def generate_traffic_camera_data(device_id, timestamp, location, camera_id):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': timestamp,
        'location': location,
        'camera_id': camera_id,
        'snapshot': 'Base64EncodedString'  # If an actual snapshot is available at a specified URL, 
                                           # the requests library can be used to fetch it and then encode it in base64.
    }


def generate_weather_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': timestamp,
        'location': location,
        'temperature': random.uniform(30, 40),
        'weather_condition': random.choice(['Sunny', 'Rainy', 'Cloudy']),
        'precipitation': random.uniform(0, 25),
        'wind_speed': random.uniform(0, 100),
        'humidity': random.randint(0, 100),
        'air_quality_index': random.uniform(0, 500)
    }


def generate_emergency_incident_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'incident_id': uuid.uuid4(),
        'timestamp': timestamp,
        'location': location,
        'type': random.choice(['Accident', 'Fire', 'Flood', 'Earthquake']),
        'status': random.choice(['Active', 'Resolved']),
        'description': 'Description of the incident'
    }

# Converts data within a dictionary that cannot be directly serialized into JSON (such as UUID) into a format that JSON supports (such as strings).
def json_serializer(obj):
    # Check if the received object (obj) is an instance of the uuid.UUID class.
    # uuid.uuid4() generates a UUID object, which is an instance of the uuid.UUID class. Each UUID object has a unique value.
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not a JSON serializable.') 
    # All data within this Python script can have the following object class names (obj.__class__.__name__): UUID, str, int, float, tuple, and etc.


def delivery_report(err, msg):  # err = error and msg = message
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
        # msg.topic() used to get the name of the topic the message was sent to.
        # msg.partition() used to get the partition number. A partition is a subpart of a topic that helps with parallelism and data distribution.


def produce_data_to_kafka(producer_parameter, topic, data):
    # Convert timestamp string to datetime object
    timestamp_dt = datetime.fromisoformat(data['timestamp'])
    # Convert datetime object to milliseconds for use as a time unit in Kafka
    timestamp_ms = int(timestamp_dt.timestamp() * 1000)
    producer_parameter.produce(
        topic,
        key=str(data['id']),
        # When sending data to Kafka, it is necessary to serialize the data (converts an object into a JSON string) using json.dumps first.
        # However, an edge case may occur where the UUID is not received correctly, which could prevent the data from being produced into Kafka.
        # Therefore, this edge case needs to be handled by modifying the data appropriately before sending it, according to the 'json_serializer(obj)' function.
        value=json.dumps(data, default=json_serializer).encode('utf-8'),
        timestamp=timestamp_ms,
        on_delivery=delivery_report
    )

    # Send the data to the Kafka broker and forces the producer to send any remaining data in the buffer immediately
    producer.flush()


def simulate_journey(producer_arg, device_id):
    while True:
        vehicle_data = generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id, vehicle_data['timestamp'])
        traffic_camera_data = generate_traffic_camera_data(device_id, vehicle_data['timestamp'], vehicle_data['location'], 'CANON')
        weather_data = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        emergency_incidence_data = generate_emergency_incident_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])

        # Check the vehicle's current location to stop the loop when it reaches Pattaya
        # ['location'][0] = latitude and ['location'][1] = longitude
        if (vehicle_data['location'][0] <= PATTAYA_COORDINATES['latitude']
                and vehicle_data['location'][1] >= PATTAYA_COORDINATES['longitude']):
            print('Vehicle has reached Pattaya. Simulation ending...')
            break

        # Sends values from these arguments to parameters in the produce_data_to_kafka() function
        produce_data_to_kafka(producer_arg, VEHICLE_TOPIC, vehicle_data)
        produce_data_to_kafka(producer_arg, GPS_TOPIC, gps_data)
        produce_data_to_kafka(producer_arg, TRAFFIC_TOPIC, traffic_camera_data)
        produce_data_to_kafka(producer_arg, WEATHER_TOPIC, weather_data)
        produce_data_to_kafka(producer_arg, EMERGENCY_TOPIC, emergency_incidence_data)

        # Pause/Sleep for approximately 5 seconds before proceeding further
        time.sleep(5)

# The following conditional statement checks if the Python file is being run directly (as the main program).
# If so, the code within this block will be executed.
# This is a common practice to separate code that should only run when the file is the main program- 
# from code that defines reusable functions or classes.
if __name__ == "__main__":
    producer_config = {
        # bootstrap.servers is a configuration value used to specify the host and port of one or more Kafka brokers, 
        # allowing Kafka clients (such as Producers or Consumers) to establish a connection to the Kafka cluster.
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        # Whenever an error occurs, this lambda function will automatically print a message to the console
        # In this case, the lambda function will receive a single argument, err, which will store the error data that occurred in Kafka.
        # Lambda functions, also known as anonymous functions, are functions that are not declared with a name. 
        # They can be used in combination with other built-in functions in Python.
        'error_cb': lambda err: print(f'Kafka error {err}')
    }
    # Creating a Producer to send messages to Kafka
    producer = SerializingProducer(producer_config)

    # Simulation Loop (try-except block)
    try:
        simulate_journey(producer, 'Vehicle-007')
    except KeyboardInterrupt:
        print('Simulation ended by the user.')
    except Exception as e:
        print(f'Unexpected error occurred: {e}')

"""
Please Note:
While this project utilizes a self-hosted Kafka instance, it's important to note that when using cloud-based Kafka solutions like Confluent Cloud, 
a username and password are required for creating and accessing producers or brokers. This authentication information is often referred to as 
SASL (Simple Authentication and Security Layer). Additionally, if you are using the Schema Registry on Confluent Cloud, the username, password, 
and host information for the Schema Registry must be included in the producer_config.
"""


"""
Test Function #1  get_next_time, simulate_journey, generate_vehicle_data

Test Function #2  get_next_time, simulate_journey, generate_vehicle_data, generate_gps_data
                  generate_traffic_camera_data, generate_weather_data, generate_emergency_incident_data

Test Function #3  get_next_time, simulate_journey, generate_vehicle_data, generate_gps_data
                  generate_traffic_camera_data, generate_weather_data, generate_emergency_incident_data
                  json_serializer, delivery_report, produce_data_to_kafka, simulate_journey

Verify that data has been successfully sent to Kafka:
1) at Terminal: show "Message delivered to ..." successfully!
2) at broker container: Exec > kafka-topics --list --bootstrap-server broker:29092
                      : Exec > kafka-console-consumer --topic vehicle_data --bootstrap-server broker:29092 --from-beginning
"""