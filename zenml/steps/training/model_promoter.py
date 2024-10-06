import json
import os
import tempfile
from uuid import UUID

import boto3
import cloudpickle
import mlflow
from mlflow.tracking import MlflowClient
from zenml import step
from zenml.client import Client
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def model_promoter(
    trained_models: dict,
    spaces_clean_version_id: UUID,
    bucket_name: str,
    models_object_key: str,
    spaces_object_key: str,
    mlflow_experiment_name: str = "model_promotion",
    mlflow_run_name: str = "production_model",
) -> None:
    """Model promoter step. Upload the model to AWS S3 and MLflow.

    Args:
        trained_models: Dict of trained models.
        spaces_clean_version_id: UUID of the spaces_clean artifact version.
        bucket_name: Name of the S3 bucket where the models should be stored.
        models_object_key: Key of the models directory in the S3 bucket.
        spaces_object_key: Key of the spaces_clean data in the S3 bucket.
        mlflow_experiment_name: Name of the MLflow experiment.
        mlflow_run_name: Name of the MLflow run.

    Returns:
        None
    """
    client = Client()
    mlflow_client = MlflowClient()

    spaces_clean_artifact_version = client.get_artifact_version(spaces_clean_version_id)
    spaces_clean = spaces_clean_artifact_version.load()

    s3 = boto3.client("s3")

    # Set up MLflow
    mlflow.set_experiment(mlflow_experiment_name)
    with mlflow.start_run(run_name=mlflow_run_name):
        with tempfile.TemporaryDirectory() as temp_dir:
            for model_name, model in trained_models.items():
                # Create a temporary file to store the model
                temp_file_path = os.path.join(temp_dir, f"{model_name}.pkl")

                # Dump the model to the temporary file
                with open(temp_file_path, "wb") as f:
                    cloudpickle.dump(model, f)

                # Upload the file to S3
                s3_key = f"{models_object_key}/{model_name}.pkl"
                try:
                    s3.upload_file(temp_file_path, bucket_name, s3_key)
                    logger.info(
                        f"Successfully uploaded model {model_name} to S3 bucket {bucket_name} with key {s3_key}"
                    )
                except Exception as e:
                    logger.error(f"Failed to upload model {model_name} to S3: {str(e)}")

                # Log model to MLflow
                try:
                    mlflow.pyfunc.log_model(
                        artifact_path=f"models/{model_name}",
                        python_model=model,
                        registered_model_name=model_name,
                    )
                    logger.info(f"Successfully logged model {model_name} to MLflow")

                    # Get the latest version of the model
                    latest_version = mlflow_client.get_latest_versions(
                        model_name, stages=["None"]
                    )[0]

                    # Add tags to the model version
                    mlflow_client.set_model_version_tag(
                        model_name,
                        latest_version.version,
                        "promoted_to_production",
                        "true",
                    )
                    mlflow_client.set_model_version_tag(
                        model_name,
                        latest_version.version,
                        "promoted_by",
                        "model_promoter_step",
                    )
                    mlflow_client.set_model_version_tag(
                        model_name, latest_version.version, "s3_bucket", bucket_name
                    )
                    mlflow_client.set_model_version_tag(
                        model_name, latest_version.version, "s3_key", s3_key
                    )

                    # Transition the model to the Production stage
                    mlflow_client.transition_model_version_stage(
                        name=model_name,
                        version=latest_version.version,
                        stage="Production",
                    )
                    logger.info(
                        f"Successfully set {model_name} version {latest_version.version} as production in MLflow"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to manage model {model_name} in MLflow: {str(e)}"
                    )

            # Upload spaces_clean data as JSON
            spaces_file_path = os.path.join(temp_dir, "spaces_clean.json")
            with open(spaces_file_path, "w") as f:
                json.dump(spaces_clean, f)

            try:
                s3.upload_file(spaces_file_path, bucket_name, spaces_object_key)
                logger.info(
                    f"Successfully uploaded spaces_clean data to S3 bucket {bucket_name} with key {spaces_object_key}"
                )
            except Exception as e:
                logger.error(f"Failed to upload spaces_clean data to S3: {str(e)}")

            # Log spaces_clean data as an artifact in MLflow
            try:
                mlflow.log_artifact(spaces_file_path, "spaces_clean")
                logger.info("Successfully logged spaces_clean data to MLflow")
            except Exception as e:
                logger.error(f"Failed to log spaces_clean data to MLflow: {str(e)}")

    logger.info("Model promotion process completed.")
