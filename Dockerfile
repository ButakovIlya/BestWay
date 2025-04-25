FROM python:3.12 as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN poetry self add poetry-plugin-export

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with=dev

FROM python:3.12

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PATH="/root/.local/bin:$PATH" \
    CELERY_APP_NAME=minecraft \
    CELERY_BROKER_URL=redis://redis:6379/0 \
    CELERY_RESULT_BACKEND=redis://redis:6379/1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN apt update
RUN apt upgrade -y
RUN apt install --no-install-recommends --no-install-suggests -y gcc libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN mkdir -p storage/media

COPY . /app
