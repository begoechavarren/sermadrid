from io import StringIO

import boto3
import pandas as pd
from typing_extensions import Annotated
from zenml import step
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def parkings_data_loader(
    bucket_name: str,
    object_key: str,
) -> Annotated[pd.DataFrame, "raw_ser_df"]:
    """Load the parking data from S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket where the data is stored.
        object_key: Key of the object in the S3 bucket.

    Returns:
        The dataset artifact as Pandas DataFrame.
    """

    s3 = boto3.client("s3")

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=object_key)
    csv_files = [
        content["Key"]
        for content in response.get("Contents", [])
        if content["Key"].endswith(".csv")
    ]
    logger.info(f"CSV files found: {csv_files}")

    logger.info("Sorting CSV files...")
    csv_files.sort()

    def standardize_columns(df):
        df.columns = df.columns.str.strip()
        replacements = {
            "cod_distrito": "codigo_distrito",
            "cod_barrio": "codigo_barrio",
        }
        df.rename(columns=replacements, inplace=True)
        return df

    dfs = []
    logger.info("Loading CSV files...")
    # TODO: Remove the slicing
    for file in csv_files[:2]:
        logger.info(f"Downloading {file}...")
        obj = s3.get_object(Bucket=bucket_name, Key=file)
        data = obj["Body"].read().decode("utf-8")

        logger.info("Defining delimiter...")
        lines = data.split("\n")
        first_line = lines[0]
        second_line = lines[1]
        rest_of_file = "\n".join(lines[2:])
        delimiter = ";" if ";" in second_line else ","
        if delimiter not in first_line:
            first_line = (
                first_line.replace(",", ";")
                if delimiter == ";"
                else first_line.replace(";", ",")
            )
        corrected_data = first_line + "\n" + second_line + "\n" + rest_of_file
        corrected_data_io = StringIO(corrected_data)

        logger.info(f"Reading {file}...")
        df = pd.read_csv(corrected_data_io, delimiter=delimiter, low_memory=False)
        df = standardize_columns(df)
        dfs.append(df)

    logger.info("Concatenating CSV files...")
    ser_df = pd.concat(dfs, ignore_index=True)
    return ser_df


@step
def spaces_data_loader(
    bucket_name: str,
    object_key: str,
) -> Annotated[pd.DataFrame, "raw_spaces_df"]:
    """Load the spaces data from S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket where the data is stored.
        object_key: Key of the object in the S3 bucket.

    Returns:
        The dataset artifact as Pandas DataFrame.
    """
    logger.info(f"Loading spaces data from S3 bucket: {bucket_name}/{object_key}")
    s3 = boto3.client("s3")
    s3_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    csv_content = s3_object["Body"].read().decode("ISO-8859-1")
    csv_file_like = StringIO(csv_content)
    raw_spaces_df = pd.read_csv(csv_file_like, delimiter=";", low_memory=False)
    return raw_spaces_df
