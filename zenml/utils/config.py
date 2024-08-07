import os
from typing import Tuple

from dotenv import load_dotenv
from zenml.client import Client
from zenml.integrations.s3.artifact_stores import S3ArtifactStore
from zenml.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
PARKINGS_LOCAL_DATA_PATH = os.getenv("PARKINGS_LOCAL_DATA_PATH")
PARKINGS_S3_DATA_PATH = os.getenv("PARKINGS_S3_DATA_PATH")
SPACES_LOCAL_DATA_PATH = os.getenv("SPACES_LOCAL_DATA_PATH")
SPACES_S3_DATA_PATH = os.getenv("SPACES_S3_DATA_PATH")


def get_data_paths() -> Tuple[str, str]:
    """
    Return the appropriate data paths based on the active ZenML stack configuration.

    Returns:
        Tuple[str, str]: Paths to the parkings and spaces data.
    """
    client = Client()
    stack = client.active_stack
    artifact_store = stack._artifact_store

    if isinstance(artifact_store, S3ArtifactStore):
        return PARKINGS_S3_DATA_PATH, SPACES_S3_DATA_PATH
    else:
        return PARKINGS_LOCAL_DATA_PATH, SPACES_LOCAL_DATA_PATH
