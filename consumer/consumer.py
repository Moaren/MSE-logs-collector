from confluent_kafka import Consumer, KafkaError
import psycopg2
import time
from dotenv import load_dotenv
import os

print("Consumer is running...")

load_dotenv(dotenv_path="/app/env/consumer.env")

NEONDB_HOST = os.getenv("NEONDB_HOST")
NEONDB_USER = os.getenv("NEONDB_USER")
NEONDB_PASSWORD = os.getenv("NEONDB_PASSWORD")
NEONDB_DATABASE = os.getenv("NEONDB_DATABASE")

# Kafka Config
consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',  # Same as kafka service in docker-compose.yml 
    'group.id': 'attack-detector-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['honeypot-traffic'])

# NeonDB Config
conn = psycopg2.connect(
    host=NEONDB_HOST,
    database=NEONDB_DATABASE,
    user=NEONDB_USER,
    password=NEONDB_PASSWORD
    # port="your_port"
)
cursor = conn.cursor()

def calculate_attack_intensity():
    count = 0
    start_time = time.time()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        # Reuqest count in one minute
        count += 1
        if time.time() - start_time >= 10: print(count)
        if time.time() - start_time >= 60:
            # Insert the result to NeonDB
            cursor.execute("INSERT INTO attack_intensity (timestamp, intensity) VALUES (%s, %s)", (time.time(), count))
            conn.commit()
            print(f"Logged intensity: {count} requests in last minute")
            count = 0
            start_time = time.time()

calculate_attack_intensity()
