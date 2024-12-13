# Используем официальный Python образ
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt /app/

# Устанавливаем все зависимости из requirements.txt
RUN pip install -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . /app/

# Открываем порт, который будет использовать Flask
EXPOSE 5000

# Команда по умолчанию будет выполняться только при запуске контейнера
CMD ["python", "/app/app.py"]
