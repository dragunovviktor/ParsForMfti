#!/bin/bash

echo "Сборка Docker образов..."
docker-compose build

echo "Запуск контейнеров..."
docker-compose up -d

echo "Ждем, пока контейнеры поднимутся..."
sleep 5

# Добавим задержку для инициализации базы данных PostgreSQL
echo "Ждем, пока PostgreSQL контейнер будет готов..."
until docker-compose exec db pg_isready -U myuser; do
  echo "Ожидание базы данных..."
  sleep 2
done
echo "PostgreSQL готова к работе!"

# Проверка на существование базы данных
echo "Проверка на существование базы данных..."
db_exists=$(docker-compose exec db psql -U myuser -tAc "SELECT 1 FROM pg_database WHERE datname='mydatabase'")

if [ "$db_exists" != "1" ]; then
  echo "База данных не существует, создаем..."
  docker-compose exec db psql -U myuser -c "CREATE DATABASE mydatabase"
else
  echo "База данных существует."
fi

# Применяем миграции Flask
echo "Создание миграций..."
docker-compose exec flask flask db migrate -m "Auto migration"

echo "Применение миграций..."
docker-compose exec flask flask db upgrade

# Запуск Flask приложения
echo "Запуск Flask приложения..."
docker-compose exec flask python /app/app.py

# Печать логов приложения
echo "Печатаем логи приложения..."
docker-compose logs -f flask

# Состояние завершения
echo "Скрипт теперь будет работать и выводить логи..."
tail -f /dev/null
