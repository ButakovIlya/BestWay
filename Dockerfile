FROM python:3.11.6-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN poetry self add poetry-plugin-export

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with=dev

FROM python:3.11.6-slim
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN apt update
RUN apt upgrade -y
RUN apt install --no-install-recommends --no-install-suggests -y gcc libc6-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app
