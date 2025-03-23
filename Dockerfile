FROM python:3.12-slim

# Настройки интерпретатора Python
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем requirements.txt
COPY ./requirements.txt /app/requirements.txt

# Обновим pip и установим зависимости из requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Копируем остальной проект
COPY . /app
