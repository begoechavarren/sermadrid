from typing import Optional
from uuid import UUID

from zenml import pipeline
from zenml.client import Client
from zenml.config import DockerSettings
from zenml.logger import get_logger

from steps.training.model_promoter import model_promoter
from steps.training.model_trainer import model_trainer

logger = get_logger(__name__)

# TODO: Want this permanently set to True?
docker_settings = DockerSettings(
    dockerfile="./zenml.dockerfile",
    build_context_root=".",
)


@pipeline(settings={"docker": docker_settings})
def training(
    final_agg_ser_df_version_id: Optional[UUID] = None,
    spaces_clean_version_id: Optional[UUID] = None,
):
    """Models training pipeline.

    Args:
        final_agg_ser_df_id: ID of the final_agg_ser_df_id dataset produced by feature engineering.
        spaces_clean_version_id: ID of the spaces_clean dataset produced by feature engineering

    Returns:
        The trained models dict (trained_models).
    """
    client = Client()
    if final_agg_ser_df_version_id is None:
        # Fetch the latest version
        artifact_versions = client.list_artifact_versions(
            name="tuned_ser_df", sort_by="created", size=1
        )
        if not artifact_versions:
            raise ValueError("No versions found for 'tuned_ser_df' artifact")
        final_agg_ser_df_version = artifact_versions[0]
    else:
        # Fetch the specified version
        final_agg_ser_df_version = client.get_artifact_version(
            final_agg_ser_df_version_id
        )

    if spaces_clean_version_id is None:
        # Fetch the latest version
        artifact_versions = client.list_artifact_versions(
            name="spaces_clean", sort_by="created", size=1
        )
        if not artifact_versions:
            raise ValueError("No versions found for 'spaces_clean' artifact")
        spaces_clean_version = artifact_versions[0]
    else:
        # Fetch the specified version
        spaces_clean_version = client.get_artifact_version(spaces_clean_version_id)

    trained_models = model_trainer(
        final_agg_ser_df_version_id=final_agg_ser_df_version.id,
    )

    # TODO: Model promoter depending on model_evaluator output
    model_promoter(
        trained_models=trained_models,
        spaces_clean_version_id=spaces_clean_version.id,
        bucket_name="sermadrid",
        # TODO: Rename to output/models/
        models_object_key="data/models",
        spaces_object_key="data/input/spaces_clean.json",
    )
