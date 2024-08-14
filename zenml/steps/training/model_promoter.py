import json
import os
import tempfile
from uuid import UUID

import boto3
import cloudpickle
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
) -> None:
    # TODO: Actually this should upload the model to a model registry,
    #  if it is locally it should be the models local directory and
    #  if it is in the cloud it should be in AWS S3
    """Model promoter step. Upload the model to AWS S3.

    Args:
        trained_models: Dict of trained models.
        bucket_name: Name of the S3 bucket where the models should be stored.
        object_key: Key of the models directory in the S3 bucket.
        spaces_object_key: Key of the spaces_clean data in the S3 bucket.

    Returns:
        Whether the model was promoted or not.
    """
    # TODO: Add ZenML functionality to store and promote models
    #  and promote them based on evaluation metrics

    client = Client()

    spaces_clean_artifact_version = client.get_artifact_version(spaces_clean_version_id)
    spaces_clean = spaces_clean_artifact_version.load()

    s3 = boto3.client("s3")

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

    logger.info("Model promotion process completed.")
