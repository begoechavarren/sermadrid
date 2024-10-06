from typing import Tuple

import pandas as pd
from zenml import Model, pipeline
from zenml.config import DockerSettings
from zenml.logger import get_logger

from steps.feature_engineering.data_aggregator import data_aggregator
from steps.feature_engineering.data_loader import (
    parkings_data_loader,
    spaces_data_loader,
)
from steps.feature_engineering.data_preprocessor import (
    parkings_data_preprocessor,
    spaces_data_preprocessor,
)
from steps.feature_engineering.data_tuner import data_tuner

logger = get_logger(__name__)

model = Model(
    name="sermadrid",
    version=None,
    license="Apache 2.0",
    description="A time series model for the sermadrid project.",
)

docker_settings = DockerSettings(
    dockerfile="./zenml.dockerfile",
    build_context_root=".",
)


@pipeline(settings={"docker": docker_settings})
def feature_engineering() -> Tuple[pd.DataFrame, dict]:
    """
    Feature engineering pipeline.

    This is a pipeline that loads the data and processes it.

    Returns:
        The processed parkings dataset (raw_ser_df).
        The processed spaces dict (spaces_clean).
    """
    raw_ser_df = parkings_data_loader()
    raw_spaces_df = spaces_data_loader()
    ser_df = parkings_data_preprocessor(
        raw_ser_df=raw_ser_df,
    )
    agg_ser_df = data_aggregator(
        ser_df=ser_df,
    )
    spaces_grouped_df, spaces_clean = spaces_data_preprocessor(
        raw_spaces_df=raw_spaces_df,
    )
    final_agg_ser_df = data_tuner(
        agg_ser_df=agg_ser_df,
        spaces_grouped_df=spaces_grouped_df,
    )
    return final_agg_ser_df, spaces_clean
