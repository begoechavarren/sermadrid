FROM python:3.11.9-slim

WORKDIR /app

RUN pip install poetry

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY zenml/pyproject.toml zenml/poetry.lock ./
COPY sermadrid /sermadrid

RUN poetry config virtualenvs.create false && poetry install --no-root

ENV ZENML_LOGGING_COLORS_DISABLED=False
ENV ZENML_ENABLE_REPO_INIT_WARNINGS=False
ENV ZENML_CONFIG_PATH=/app/.zenconfig

RUN chmod -R a+rw .

RUN echo '#!/bin/sh\n\
zenml init\n\
zenml up --port $ZENML_SERVER_PORT --ip-address 0.0.0.0 &\n\
sleep 10\n\
zenml create-user --name $ZENML_DEFAULT_USERNAME --password $ZENML_DEFAULT_PASSWORD --role admin || true\n\
tail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8080

ENTRYPOINT ["/app/start.sh"]