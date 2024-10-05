import pandas as pd
from typing_extensions import Annotated
from zenml import step
from zenml.logger import get_logger

from utils.config import get_data_paths
from utils.data_loader import standardize_parking_columns
from utils.data_sources import get_data_source

logger = get_logger(__name__)

logger.info("Loading data...")
DATA_SOURCE = get_data_source()
PARKINGS_DATA_PATH, SPACES_DATA_PATH = get_data_paths()


@step
def parkings_data_loader() -> Annotated[pd.DataFrame, "raw_ser_df"]:
    """
    Load the parking data from the configured data source, in
    an agnostic way to the data source.

    Args:
        path: Path where the parkings data is stored.

    Returns:
        The parkings dataset as a Pandas DataFrame.
    """
    logger.info(f"Loading data from {DATA_SOURCE} at {PARKINGS_DATA_PATH}...")
    csv_file_paths = DATA_SOURCE.list_csv_files(PARKINGS_DATA_PATH)
    logger.info(
        f"Found this number of CSV files {len(csv_file_paths)}: {csv_file_paths}"
    )

    dfs = []
    for file_path in csv_file_paths:
        logger.info(f"Loading {file_path}...")
        df = DATA_SOURCE.load_csv(
            file_path=file_path,
            delimiter=";",
            encoding="UTF-8",
        )
        df = standardize_parking_columns(df)
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


@step
def spaces_data_loader() -> Annotated[pd.DataFrame, "raw_spaces_df"]:
    """Load the spaces data from the configured data source, in

    Args:
        file_path: Path where the spaces data is stored.

    Returns:
        The dataset artifact as Pandas DataFrame.
    """
    logger.info(f"Spaces data path: {SPACES_DATA_PATH}")
    # TODO: Fix S3DataSource load_csv function
    return DATA_SOURCE.load_csv(
        SPACES_DATA_PATH,
        delimiter=";",
        encoding="ISO-8859-1",
    )
