# Используем базовый образ для Go
FROM golang:1.23

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем go.mod и go.sum, чтобы установить зависимости
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходный код
COPY . .

# Сборка приложения
RUN go build -o app .

# Указываем команду для запуска
CMD ["./app"]

