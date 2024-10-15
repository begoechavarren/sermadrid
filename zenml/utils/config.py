import os
from typing import Tuple

from dotenv import load_dotenv
from zenml.client import Client
from zenml.integrations.s3.artifact_stores import S3ArtifactStore
from zenml.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


secrets = Client().list_secrets().items
secret_names = [secret.name for secret in secrets]
if "aws" not in secret_names:
    Client().create_secret(
        "aws",
        {
            "S3_BUCKET_NAME": os.getenv("S3_BUCKET_NAME"),
            "PARKINGS_LOCAL_DATA_PATH": os.getenv("PARKINGS_LOCAL_DATA_PATH"),
            "PARKINGS_S3_DATA_PATH": os.getenv("PARKINGS_S3_DATA_PATH"),
            "SPACES_LOCAL_DATA_PATH": os.getenv("SPACES_LOCAL_DATA_PATH"),
            "SPACES_S3_DATA_PATH": os.getenv("SPACES_S3_DATA_PATH"),
        },
    )


def get_data_paths() -> Tuple[str, str]:
    """
    Return the appropriate data paths based on the active ZenML stack configuration.

    Returns:
        Tuple[str, str]: Paths to the parkings and spaces data.
    """
    client = Client()
    stack = client.active_stack
    artifact_store = stack._artifact_store
    secret_values = client.get_secret("aws").secret_values

    if isinstance(artifact_store, S3ArtifactStore):
        parkings_s3_data_path = secret_values["PARKINGS_S3_DATA_PATH"]
        spaces_s3_data_path = secret_values["SPACES_S3_DATA_PATH"]
        return parkings_s3_data_path, spaces_s3_data_path
    else:
        parkings_local_data_path = secret_values["PARKINGS_LOCAL_DATA_PATH"]
        spaces_local_data_path = secret_values["SPACES_LOCAL_DATA_PATH"]
        return parkings_local_data_path, spaces_local_data_path
