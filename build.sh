#!/bin/bash

echo "Сборка Docker образов..."
echo "Открываем бутылку пива"
docker-compose build

echo "Запуск контейнеров..."
echo "Можно пить"
docker-compose up -d

echo "Ждем, пока контейнеры поднимутся..."
sleep 5

echo "Создание миграций..."
docker-compose exec flask flask db migrate -m "Auto migration"

echo "Применение миграций..."
docker-compose exec flask flask db upgrade

echo "Печатаем логи приложения..."
docker-compose logs -f flask

echo "Скрипт теперь будет работать и выводить логи..."
tail -f /dev/null
