from uuid import UUID

from tqdm import tqdm
from typing_extensions import Annotated
from zenml import step
from zenml.client import Client
from zenml.logger import get_logger

from sermadrid.sermadrid.models import CustomProphetModelNH

logger = get_logger(__name__)


# TODO: Set enable_cache to True?
@step(enable_cache=True)
def model_trainer(
    final_agg_ser_df_version_id: UUID,
) -> Annotated[dict, "trained_models"]:
    """Train the models on the final_agg_ser_df dataset.

    Args:
        final_agg_ser_df: The final aggregated ser dataset.

    Returns:
        The trained models dict.
    """
    logger.info("Training models...")

    client = Client()

    artifact_version = client.get_artifact_version(final_agg_ser_df_version_id)
    final_agg_ser_df = artifact_version.load()

    trained_models = {}

    for barrio_id in tqdm(final_agg_ser_df["barrio_id"].unique()):
        logger.info(f"Training model for barrio with barrio_id {barrio_id}")
        model = CustomProphetModelNH(
            barrio_id=barrio_id,
        )
        model.train(
            agg_df=final_agg_ser_df,
        )
        logger.info(f"Model trained for barrio with barrio_id {barrio_id}")

        trained_models[barrio_id] = model

    return trained_models
