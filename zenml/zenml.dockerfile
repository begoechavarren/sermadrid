FROM python:3.11.9-slim

WORKDIR /app

# Create a startup script
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

echo "Starting container initialization..."

# Set up AWS configuration to use /tmp
export AWS_CONFIG_FILE=/tmp/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=/tmp/.aws/credentials
export HOME=/tmp

# Create necessary directories
mkdir -p /tmp/.aws
mkdir -p /tmp/.zenconfig

# Configure AWS CLI if needed
if [ ! -f "$AWS_CONFIG_FILE" ]; then
    aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile default --config-file $AWS_CONFIG_FILE
    aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile default --config-file $AWS_CONFIG_FILE
    aws configure set region "$AWS_REGION" --profile default --config-file $AWS_CONFIG_FILE
    echo "AWS CLI configured successfully."
fi

# Redirect all ZenML connection output to stdout
echo "Connecting to ZenML server at: ${ZENML_SERVER_URL}"
zenml connect --url="${ZENML_SERVER_URL}" --api-key="${ZENML_API_KEY}"
echo "Listing ZenML stacks:"
zenml stack list
echo "Setting ZenML stack to sermadrid"
zenml stack set "sermadrid"
echo "Final stack list:"
zenml stack list
echo "Register ZenML service connector"
zenml service-connector register kube-auto --type kubernetes --auto-configure
zenml artifact-store connect s3_artifact_store --connector kube-auto
zenml container-registry connect ecr_registry --connector kube-auto
zenml orchestrator connect k8s_orchestrator --connector kube-auto
zenml experiment-tracker connect mlflow_tracker --connector kube-auto

# Execute the Lambda handler
exec python3 -m awslambdaric lambda_handler.lambda_handler
EOF

RUN chmod +x /app/start.sh

RUN apt-get update && apt-get install -y awscli

RUN pip install awslambdaric poetry

RUN mkdir -p zenml

COPY sermadrid /sermadrid
COPY zenml/pyproject.toml zenml/poetry.lock ./
COPY zenml/pipelines ./pipelines
COPY zenml/steps ./steps
COPY zenml/utils ./utils
COPY zenml/lambda_handler.py ./

# Create necessary directories with proper permissions
RUN mkdir -p /tmp/.aws /tmp/.zenconfig && \
    chmod 777 /tmp/.aws /tmp/.zenconfig

RUN poetry config virtualenvs.create false && \
    poetry install --no-root && \
    poetry show

ENV PYTHONUNBUFFERED=1
ENV ZENML_LOGGING_COLORS_DISABLED=False
ENV ZENML_ENABLE_REPO_INIT_WARNINGS=False
ENV ZENML_CONFIG_PATH=/tmp/.zenconfig
ENV HOME=/tmp

# Other environment variables
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION
ARG S3_BUCKET_NAME
ARG ZENML_STACK_ENV
ARG PARKINGS_S3_DATA_PATH
ARG SPACES_S3_DATA_PATH

# ZenML connection setup
ARG ZENML_SERVER_URL
ARG ZENML_API_KEY

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    AWS_REGION=${AWS_REGION} \
    S3_BUCKET_NAME=${S3_BUCKET_NAME} \
    ZENML_STACK_ENV=${ZENML_STACK_ENV} \
    PARKINGS_S3_DATA_PATH=${PARKINGS_S3_DATA_PATH} \
    SPACES_S3_DATA_PATH=${SPACES_S3_DATA_PATH}

# Use the startup script instead of direct command
ENTRYPOINT ["/app/start.sh"]