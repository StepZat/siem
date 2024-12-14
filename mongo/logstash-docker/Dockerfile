# Используем официальный образ Logstash
FROM logstash:8.10.2

# Устанавливаем плагин logstash-output-mongodb
RUN bin/logstash-plugin install --version 3.1.5 logstash-output-mongodb

# Копируем конфигурационные файлы Logstash в контейнер
# Предполагается, что logstash.conf находится в директории ./pipeline
COPY ./logstash.conf /usr/share/logstash/pipeline/logstash.conf

# Указываем рабочую директорию
WORKDIR /usr/share/logstash

# Открываем порты, если требуется (API Logstash для мониторинга)
EXPOSE 5044 9600

# Указываем команду по умолчанию для запуска Logstash
CMD ["logstash"]
