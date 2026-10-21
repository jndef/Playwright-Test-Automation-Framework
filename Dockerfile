FROM mcr.microsoft.com/playwright/python:v1.62.0-noble
FROM python:3.14.6-slim-trixie
ARG ALLURE_VERSION=2.35.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless curl tar && \
    curl -o allure-${ALLURE_VERSION}.tgz -Ls https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.tgz && \
    tar -zxvf allure-${ALLURE_VERSION}.tgz -C /opt/ && \
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/bin/allure && \
    rm allure-${ALLURE_VERSION}.tgz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# Устанавливаем рабочую директорию
WORKDIR /usr/workspace

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium
# Копируем весь проект
COPY . .

# Команда по умолчанию
CMD ["pytest", "-m", "smoke", "--headed"]