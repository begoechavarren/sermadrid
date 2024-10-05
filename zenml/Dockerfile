# Use the specified ZenML image as the base image
FROM zenmldocker/zenml:0.67.0-py3.11

# Set the working directory in the container
WORKDIR /app

# Copy the sermadrid directory first for dependency installation
COPY sermadrid/ ./sermadrid/

# Copy the dependency files for caching purposes
COPY pyproject.toml poetry.lock ./

# Upgrade pip and setuptools, and install Poetry
RUN pip install --upgrade pip setuptools \
    && pip install poetry

# Print Poetry configuration for debugging
RUN poetry config --list

# Run poetry check to ensure pyproject.toml is correct
RUN poetry check || true

# Install dependencies (this step is cached unless pyproject.toml or poetry.lock change)
RUN poetry config virtualenvs.create false \
    && poetry install

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV ZENML_LOGGING_COLORS_DISABLED=False
ENV ZENML_ENABLE_REPO_INIT_WARNINGS=False
ENV ZENML_CONFIG_PATH=/app/.zenconfig

# Set environment variables from build arguments
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_REGION=$AWS_REGION
ENV S3_BUCKET_NAME=$S3_BUCKET_NAME
ENV ZENML_STACK_ENV=$ZENML_STACK_ENV
ENV PARKINGS_S3_DATA_PATH=$PARKINGS_S3_DATA_PATH
ENV SPACES_S3_DATA_PATH=$SPACES_S3_DATA_PATH

# Ensure that the files have the appropriate permissions
RUN chmod -R a+rw .
