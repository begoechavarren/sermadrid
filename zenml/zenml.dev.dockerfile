# Use Python 3.11.9 as the base image
FROM python:3.11.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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

# Ensure that the files have the appropriate permissions
RUN chmod -R a+rw .

# Create a startup script
RUN echo '#!/bin/sh\n\
zenml init\n\
zenml up --port $ZENML_SERVER_PORT --ip-address 0.0.0.0 &\n\
sleep 10\n\
zenml create-user --name $ZENML_DEFAULT_USERNAME --password $ZENML_DEFAULT_PASSWORD --role admin || true\n\
tail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

# Expose the port that ZenML server will run on
EXPOSE 8080

# Set the startup script as the entry point
ENTRYPOINT ["/app/start.sh"]