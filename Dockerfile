# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем FFmpeg для конвертации видео и создания превью
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем необходимые директории в /data (persistent mount)
RUN mkdir -p /data/media/videos /data/media/thumbnails

# Даём права на запись
RUN chmod -R 755 /data

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]