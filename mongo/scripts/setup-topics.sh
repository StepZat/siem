#!/bin/bash

# Ждём Kafka, чтобы она была готова
echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 9092; do   
  sleep 1
done
echo "Kafka is ready!"

# Создаём топики
echo "Creating topics..."
kafka-topics --create --bootstrap-server kafka:9092 \
  --replication-factor 1 --partitions 3 --topic radius || echo "Topic 'radius' already exists"

kafka-topics --create --bootstrap-server kafka:9092 \
  --replication-factor 1 --partitions 3 --topic default || echo "Topic 'default' already exists"

echo "Topics created successfully!"
