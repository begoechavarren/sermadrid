```bash
# Install required zenml integrations
zenml integration install sklearn -y

# Initialize ZenML
zenml init

# Start the ZenServer to enable dashboard access
zenml up

# Run the feature engineering pipeline
python run.py --feature-pipeline

# Run the training pipeline
python run.py --training-pipeline

# Run the training pipeline with versioned artifacts
python run.py --training-pipeline --train-dataset-version-name=1 --test-dataset-version-name=1

# Run the inference pipeline
python run.py --inference-pipeline
