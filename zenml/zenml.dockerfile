FROM zenmldocker/zenml:0.66.0-py3.11

WORKDIR /app

RUN pip install poetry

COPY zenml/pyproject.toml pyproject.toml
COPY zenml/poetry.lock poetry.lock
COPY sermadrid /sermadrid

RUN poetry config virtualenvs.create false && \
    poetry install --no-root

COPY zenml /app/zenml

ENV ZENML_LOGGING_COLORS_DISABLED=False \
    ZENML_ENABLE_REPO_INIT_WARNINGS=False \
    ZENML_CONFIG_PATH=/app/.zenconfig

RUN chmod -R a+rw .

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION
ARG S3_BUCKET_NAME
ARG ZENML_STACK_ENV
ARG PARKINGS_S3_DATA_PATH
ARG SPACES_S3_DATA_PATH

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    AWS_REGION=${AWS_REGION} \
    S3_BUCKET_NAME=${S3_BUCKET_NAME} \
    ZENML_STACK_ENV=${ZENML_STACK_ENV} \
    PARKINGS_S3_DATA_PATH=${PARKINGS_S3_DATA_PATH} \
    SPACES_S3_DATA_PATH=${SPACES_S3_DATA_PATH}
