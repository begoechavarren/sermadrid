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


@step(enable_cache=False)
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
    # Set MLflow tracking URI
    os.environ[
        "MLFLOW_TRACKING_URI"
    ] = client.active_stack.experiment_tracker.config.tracking_uri
    logger.info(f"MLflow tracking URI set to: {mlflow.get_tracking_uri()}")

    # Log current working directory and environment variables
    logger.info(f"Current working directory: {os.getcwd()}")

    client = Client()
    mlflow_client = MlflowClient(tracking_uri=mlflow.get_tracking_uri())

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

                    model_info = mlflow.pyfunc.log_model(
                        artifact_path=f"models/{model_name}",
                        python_model=wrapped_model,
                        conda_env=conda_env,
                        registered_model_name=str(model_name),
                    )
                    logger.info(
                        f"Model logged successfully. Model URI: {model_info.model_uri}"
                    )

                    # Get the latest version of the model
                    latest_version = mlflow_client.search_model_versions(
                        f"name='{model_name}'"
                    )[0]

                    # Add tags to the model version
                    mlflow_client.set_model_version_tag(
                        name=str(model_name),
                        version=latest_version.version,
                        key="s3_path",
                        value={
                            "bucket_name": bucket_name,
                            "s3_key": s3_key,
                        },
                    )
                    mlflow_client.set_model_version_tag(
                        name=str(model_name),
                        version=latest_version.version,
                        key="stage",
                        value="production",
                    )

                    # Set the 'champion' alias for the latest version
                    mlflow_client.set_registered_model_alias(
                        name=str(model_name),
                        alias="champion",
                        version=latest_version.version,
                    )
                    logger.info(
                        f"Successfully set {model_name} version {latest_version.version} as 'champion' in MLflow"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to manage model {model_name} in MLflow: {str(e)}"
                    )
                    logger.exception("Full traceback:")

            # Log spaces_clean data to MLflow as an artifact
            try:
                spaces_file_path = os.path.join(temp_dir, "spaces_clean.json")
                with open(spaces_file_path, "w") as f:
                    json.dump(spaces_clean, f)

                # Upload to S3
                try:
                    s3.upload_file(spaces_file_path, bucket_name, spaces_object_key)
                    logger.info(
                        f"Successfully uploaded spaces_clean data to S3 bucket {bucket_name} with key {spaces_object_key}"
                    )
                except Exception as e:
                    logger.error(f"Failed to upload spaces_clean data to S3: {str(e)}")
                    logger.exception("Full traceback:")

                # Log to MLflow as an artifact
                mlflow.log_artifact(spaces_file_path, "spaces_clean")
                logger.info(
                    "Successfully logged spaces_clean data to MLflow as an artifact"
                )

                # Log S3 path as a parameter
                mlflow.log_param("spaces_clean_s3_bucket", bucket_name)
                mlflow.log_param("spaces_clean_s3_key", spaces_object_key)

                # Tag this run as the production version for spaces_clean
                mlflow_client.set_tag(
                    run.info.run_id, "spaces_clean_production", "true"
                )

                # Untag the previous production version
                experiment = mlflow_client.get_experiment_by_name(
                    mlflow_experiment_name
                )
                if experiment:
                    previous_prod_runs = mlflow_client.search_runs(
                        experiment_ids=[experiment.experiment_id],
                        filter_string="tags.spaces_clean_production = 'true'",
                        max_results=1,
                        order_by=["attribute.start_time DESC"],
                    )
                    for prev_run in previous_prod_runs:
                        if prev_run.info.run_id != run.info.run_id:
                            mlflow_client.set_tag(
                                prev_run.info.run_id, "spaces_clean_production", "false"
                            )
                            logger.info(
                                f"Untagged previous production spaces_clean in run {prev_run.info.run_id}"
                            )

                logger.info(
                    f"Tagged current run {run.info.run_id} as production for spaces_clean"
                )

            except Exception as e:
                logger.error(f"Failed to log spaces_clean data to MLflow: {str(e)}")
                logger.exception("Full traceback:")

    logger.info("Model promotion process completed.")
