import os
from abc import ABC, abstractmethod
from io import StringIO
from typing import List, Optional

import boto3
import pandas as pd
from zenml.client import Client
from zenml.integrations.s3.artifact_stores import S3ArtifactStore
from zenml.logger import get_logger

logger = get_logger(__name__)


class DataSource(ABC):
    """
    Abstract base class for different data sources.

    Methods:
        load_csv: Load a CSV file.
        list_files: List all files in a given path.
    """

    @abstractmethod
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load a CSV file.

        Args:
            file_path: Path to the CSV file.

        Returns:
            DataFrame containing the CSV data.
        """
        pass

    @abstractmethod
    def list_csv_files(self, path: str, delimiter: Optional[str] = None) -> List[str]:
        """
        List all CSV files in a given path.

        Args:
            path: Path to the directory containing the CSV files.
            delimiter: Delimiter to use in the CSV files.

        Returns:
            List of paths to the CSV files.
        """
        pass


class LocalDataSource(DataSource):
    """
    Data source for loading local CSV files.
    """

    @staticmethod
    def _fix_delimiter(file_path: str) -> StringIO:
        """
        Fix the delimiter of a CSV file.

        Args:
            file_path: Path to the CSV file.

        Returns:
            StringIO object with fixed delimiter.
        """
        with open(file_path, "r") as file:
            first_line = file.readline()
            second_line = file.readline()
            rest_of_file = file.read()
        delimiter = ";" if ";" in second_line else ","
        if delimiter not in first_line:
            first_line = (
                first_line.replace(",", ";")
                if delimiter == ";"
                else first_line.replace(";", ",")
            )
        return StringIO(first_line + "\n" + second_line + "\n" + rest_of_file)

    def load_csv(
        self,
        file_path: str,
        encoding: str,
        delimiter: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load a CSV file from the local file system.

        Args:
            file_path: Path to the CSV file.
            encoding: Encoding of the CSV file.
            delimiter: Delimiter of the CSV file.

        Returns:
            DataFrame containing the CSV data.
        """
        file_path_or_buffer = (
            self._fix_delimiter(file_path) if encoding == "UTF-8" else file_path
        )

        df = pd.read_csv(
            file_path_or_buffer,
            delimiter=delimiter,
            encoding=encoding,
            low_memory=False,
        )
        return df

    def list_csv_files(
        self,
        path: str,
    ) -> List[str]:
        """
        List all CSV files in a given path.

        Args:
            path: Path to the directory containing the CSV files.

        Returns:
            List of paths to the CSV files.
        """
        csv_file_paths = [
            os.path.join(path, file)
            for file in os.listdir(path)
            if file.endswith(".csv")
        ]
        logger.info(f"Found the following files in path {path}: {csv_file_paths}")
        return csv_file_paths


class S3DataSource(DataSource):
    """
    Data source for loading CSV files from an S3 bucket.

    Attributes:
        bucket_name: Name of the S3 bucket.
    """

    def __init__(self, bucket_name: str):
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def load_csv(
        self, file_path: str, encoding: str, delimiter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load a CSV file from the S3 bucket.

        Args:
            file_path: Path to the CSV file in the S3 bucket.
            encoding: Encoding of the CSV file.

        Returns:
            DataFrame containing the CSV data.
        """
        logger.info(f"Loading {file_path} from S3 bucket {self.bucket_name}...")
        obj = self.s3.get_object(Bucket=self.bucket_name, Key=file_path)
        csv_content = obj["Body"].read().decode(encoding)
        return pd.read_csv(StringIO(csv_content))

    def list_csv_files(self, path: str) -> List[str]:
        """
        List all files in a given path in the S3 bucket.

        Args:
            path: Path to the directory in the S3 bucket.

        Returns:
            List of paths to the files in the S3 bucket.
        """
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=path)
        return [
            content["Key"]
            for content in response.get("Contents", [])
            if content["Key"].endswith(".csv")
        ]


def get_data_source() -> DataSource:
    """
    Factory method to determine the appropriate data source based on
    the active ZenML stack configuration.

    Returns:
        An instance of `LocalDataSource` or `S3DataSource` based on the
            active ZenML stack configuration.
    """
    from utils.config import S3_BUCKET_NAME

    client = Client()
    stack = client.active_stack
    artifact_store = stack._artifact_store

    if isinstance(artifact_store, S3ArtifactStore):
        logger.info(f"Using S3DataSource with bucket: {S3_BUCKET_NAME}")
        return S3DataSource(S3_BUCKET_NAME)

    logger.info("Using LocalDataSource")
    return LocalDataSource()
