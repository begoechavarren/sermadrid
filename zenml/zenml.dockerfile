FROM zenmldocker/zenml:0.66.0-py3.11

WORKDIR /app

RUN pip install poetry

COPY zenml/pyproject.toml zenml/poetry.lock ./
COPY sermadrid /sermadrid

RUN poetry config virtualenvs.create false && poetry install --no-root

ENV ZENML_LOGGING_COLORS_DISABLED=False
ENV ZENML_ENABLE_REPO_INIT_WARNINGS=False
ENV ZENML_CONFIG_PATH=/app/.zenconfig

RUN chmod -R a+rw .

# Set environment variables from build arguments
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_REGION=$AWS_REGION
ENV S3_BUCKET_NAME=$S3_BUCKET_NAME
ENV ZENML_STACK_ENV=$ZENML_STACK_ENV
ENV PARKINGS_S3_DATA_PATH=$PARKINGS_S3_DATA_PATH
ENV SPACES_S3_DATA_PATH=$SPACES_S3_DATA_PATH