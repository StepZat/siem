package main

import (
	"log"
	"os"

	"github.com/hpcloud/tail"
	"github.com/confluentinc/confluent-kafka-go/kafka"
)

func main() {
	// Получаем переменные окружения
	kafkaBroker := os.Getenv("KAFKA_BROKER")
	kafkaTopic := os.Getenv("KAFKA_TOPIC")
	logFilePath := os.Getenv("LOG_FILE_PATH")

	if kafkaBroker == "" || kafkaTopic == "" || logFilePath == "" {
		log.Fatal("KAFKA_BROKER, KAFKA_TOPIC, and LOG_FILE_PATH must be set")
	}

	// Проверяем, что файл существует
	if _, err := os.Stat(logFilePath); os.IsNotExist(err) {
		log.Fatalf("Log file does not exist: %s", logFilePath)
	}

	// Создаем Kafka-продюсер
	producer, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": kafkaBroker})
	if err != nil {
		log.Fatalf("Failed to create Kafka producer: %s", err)
	}
	defer producer.Close()

	// Используем hpcloud/tail для чтения файла
	t, err := tail.TailFile(logFilePath, tail.Config{
	    	Follow: true,
		ReOpen: true,
		Location: &tail.SeekInfo{
        		Offset: 0,
        		Whence: 2, // 2 означает SEEK_END - начать с конца файла
	    	},
	})
	if err != nil {
		log.Fatalf("Failed to tail file: %s", err)
	}

	log.Printf("Reading logs from file: %s", logFilePath)

	// Читаем новые строки из файла и отправляем их в Kafka
	for line := range t.Lines {
		if line.Err != nil {
			log.Printf("Error reading line: %s", line.Err)
			continue
		}

		log.Printf("Sending log to Kafka: %s", line.Text)

		err := producer.Produce(&kafka.Message{
			TopicPartition: kafka.TopicPartition{Topic: &kafkaTopic, Partition: kafka.PartitionAny},
			Value:          []byte(line.Text),
		}, nil)

		if err != nil {
			log.Printf("Failed to send log to Kafka: %s", err)
		}
	}

	// Ожидаем завершения отправки всех сообщений перед завершением программы
	producer.Flush(15 * 1000)
}

