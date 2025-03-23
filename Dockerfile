FROM python:3.12

# Настройки интерпретатора Python
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY ./requirements.txt /app/requirements.txt

# Установка системных пакетов (минимально)
RUN apt update \
    && apt upgrade -y \
    && apt install --no-install-recommends --no-install-suggests -y gcc libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Копируем весь проект
COPY . /app
