import json
import tempfile
from uuid import UUID

import boto3
import cloudpickle
from zenml import step
from zenml.client import Client
from zenml.logger import get_logger

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
from sermadrid.sermadrid.models import CustomProphetWrapper

logger = get_logger(__name__)


@step(enable_cache=True)
def model_promoter(
    trained_models: dict,
    spaces_clean_version_id: UUID,
    bucket_name: str,
    models_object_key: str,
    spaces_object_key: str,
    mlflow_experiment_name: str = "model_promotion",
    mlflow_run_name: str = "production_model",
) -> None:
    """Model promoter step. Upload the model to AWS S3 and MLflow."""

    import os

    client = Client()
    os.environ[
        "MLFLOW_TRACKING_URI"
    ] = client.active_stack.experiment_tracker.config.tracking_uri

    # # Set MLflow tracking URI
    # mlflow_uri = os.environ.get('MLFLOW_TRACKING_URI', "http://localhost:5000")
    # mlflow.set_tracking_uri(mlflow_uri)
    logger.info(f"MLflow tracking URI set to: {mlflow.get_tracking_uri()}")

    # Log current working directory and environment variables
    logger.info(f"Current working directory: {os.getcwd()}")

    client = Client()
    mlflow_client = MlflowClient(tracking_uri=mlflow.get_tracking_uri())

    # # Log MLflow client details
    # logger.info(f"MLflow client tracking URI: {mlflow_client.tracking_uri}")

    spaces_clean_artifact_version = client.get_artifact_version(spaces_clean_version_id)
    spaces_clean = spaces_clean_artifact_version.load()

    s3 = boto3.client("s3")

    # Set up MLflow
    mlflow.set_experiment(mlflow_experiment_name)
    logger.info(f"MLflow experiment set to: {mlflow_experiment_name}")

    # List all experiments
    experiments = mlflow.search_experiments()
    for exp in experiments:
        logger.info(f"Available experiment: Name: {exp.name}, ID: {exp.experiment_id}")

    with mlflow.start_run(run_name=mlflow_run_name) as run:
        logger.info(f"Started MLflow run: {run.info.run_id}")

        logger.info(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
        logger.info(f"MLflow artifact URI: {mlflow.get_artifact_uri()}")
        logger.info(
            f"MLflow current experiment: {mlflow.get_experiment(mlflow.active_run().info.experiment_id).name}"
        )

        # Log artifact repository details
        artifact_uri = mlflow.get_artifact_uri()
        logger.info(f"Artifact URI: {artifact_uri}")

        with tempfile.TemporaryDirectory() as temp_dir:
            for model_name, model in trained_models.items():
                logger.info(f"Processing model: {model_name}")

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
                    logger.exception("Full traceback:")

                # Log model to MLflow
                try:
                    logger.info(f"Starting to log model {model_name} to MLflow")
                    wrapped_model = CustomProphetWrapper(model)

                    # Create a conda environment file
                    conda_env = mlflow.pyfunc.get_default_conda_env()
                    conda_env["dependencies"].extend(["prophet", "workalendar"])

                    model_info = mlflow.pyfunc.log_model(
                        artifact_path=f"models/{model_name}",
                        python_model=wrapped_model,
                        conda_env=conda_env,
                        registered_model_name=str(model_name),
                    )
                    logger.info(
                        f"Model logged successfully. Model URI: {model_info.model_uri}"
                    )

                    logger.info(f"Successfully logged model {model_name} to MLflow")

                    # Get the latest version of the model
                    latest_version = mlflow_client.get_latest_versions(
                        str(model_name), stages=["None"]
                    )[0]

                    # Add tags to the model version
                    mlflow_client.set_model_version_tag(
                        str(model_name),
                        latest_version.version,
                        "promoted_to_production",
                        "true",
                    )
                    mlflow_client.set_model_version_tag(
                        str(model_name),
                        latest_version.version,
                        "promoted_by",
                        "model_promoter_step",
                    )
                    mlflow_client.set_model_version_tag(
                        str(model_name),
                        latest_version.version,
                        "s3_bucket",
                        bucket_name,
                    )
                    mlflow_client.set_model_version_tag(
                        str(model_name), latest_version.version, "s3_key", s3_key
                    )

                    # Transition the model to the Production stage
                    mlflow_client.transition_model_version_stage(
                        name=str(model_name),
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
                    logger.exception("Full traceback:")

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
                logger.exception("Full traceback:")

            # Log spaces_clean data as an artifact in MLflow
            try:
                mlflow.log_artifact(spaces_file_path, "spaces_clean")
                logger.info("Successfully logged spaces_clean data to MLflow")
            except Exception as e:
                logger.error(f"Failed to log spaces_clean data to MLflow: {str(e)}")
                logger.exception("Full traceback:")

    logger.info("Model promotion process completed.")
