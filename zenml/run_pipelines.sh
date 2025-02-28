#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ZENML_SERVER_URL="http://localhost:8081"
MLFLOW_TRACKING_URI="http://localhost:5000"

# Source the .env file from the parent directory of the script
source "$SCRIPT_DIR/../.env"

# Connect to the ZenML server
echo "Connecting to ZenML server..."
echo $ZENML_SERVER_URL
zenml connect --url $ZENML_SERVER_URL
if [ $? -ne 0 ]; then
    echo "Failed to connect to ZenML server. Exiting."
    exit 1
fi

# Register MLflow tracking server
echo "Registering/Updating MLflow tracking server..."
zenml experiment-tracker register mlflow_tracker \
    --flavor=mlflow \
    --tracking_uri=$MLFLOW_TRACKING_URI \
    --tracking_username=$MLFLOW_USERNAME \
    --tracking_password=$MLFLOW_PASSWORD

# Create a new stack with the default components and the new MLflow tracker
echo "Creating new stack '$ZENML_NEW_STACK_NAME'..."
zenml stack register $ZENML_NEW_STACK_NAME \
    -o default \
    -a default \
    -e mlflow_tracker

# Set the new stack as active
echo "Setting '$ZENML_NEW_STACK_NAME' as the active stack..."
zenml stack set $ZENML_NEW_STACK_NAME
zenml stack list

# Run the zenml pipelines
python "$SCRIPT_DIR/run.py" --feature-pipeline
python "$SCRIPT_DIR/run.py" --training-pipeline