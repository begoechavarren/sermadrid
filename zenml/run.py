from typing import Optional
from uuid import UUID

import click
import zenml
from zenml.client import Client
from zenml.logger import get_logger

from pipelines.feature_engineering import feature_engineering
from pipelines.training import training

logger = get_logger(__name__)


@click.command(
    help="""
ZenML sermadrid project.

Run the ZenML sermadrid pipelines:

  \b
  # Run the feature engineering pipeline
    python run.py --feature-pipeline

  \b
  # Run the training pipeline
    python run.py --training-pipeline

  \b
  # Run both pipelines
    python run.py --feature-pipeline --training-pipeline

  \b
  # Run the training pipeline with versioned artifacts
    python run.py --training-pipeline --final-agg-ser-df-version-id=<id> --spaces-clean-version-id=<id>

  \b
  # Run without cache
    python run.py --feature-pipeline --training-pipeline --no-cache
"""
)
@click.option(
    "--final-agg-ser-df-name",
    default="tuned_ser_df",
    type=click.STRING,
    help="The name of the SER dataset produced by feature engineering.",
)
@click.option(
    "--spaces-clean-name",
    default="spaces_clean",
    type=click.STRING,
    help="The name of the spaces dict produced by feature engineering.",
)
@click.option(
    "--trained-models-name",
    default="trained_models",
    type=click.STRING,
    help="The name of the trained models dict produced by training.",
)
@click.option(
    "--final-agg-ser-df-version-id",
    default=None,
    type=click.STRING,
    help="ID of the final aggregated SER dataset version. If not specified, the latest version will be used.",
)
@click.option(
    "--spaces-clean-version-id",
    default=None,
    type=click.STRING,
    help="ID of the spaces dict version. If not specified, the latest version will be used.",
)
@click.option(
    "--feature-pipeline",
    is_flag=True,
    default=False,
    help="Run the pipeline that creates the dataset.",
)
@click.option(
    "--training-pipeline",
    is_flag=True,
    default=False,
    help="Run the pipeline that trains the model.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
def main(
    final_agg_ser_df_name: str,
    spaces_clean_name: str,
    trained_models_name: str,
    final_agg_ser_df_version_id: Optional[UUID],
    spaces_clean_version_id: Optional[UUID],
    feature_pipeline: bool,
    training_pipeline: bool,
    no_cache: bool,
):
    print("ZenML version", zenml.__version__)
    client = Client()

    pipeline_args = {"enable_cache": not no_cache}

    if feature_pipeline:
        feature_engineering.with_options(**pipeline_args)()
        logger.info("Feature Engineering pipeline finished successfully!")

        final_agg_ser_df_artifact = client.get_artifact_version(final_agg_ser_df_name)
        spaces_clean_artifact = client.get_artifact_version(spaces_clean_name)

        logger.info(
            f"Feature engineering pipeline produced:\n"
            f"1. SER dataset - Name: {final_agg_ser_df_name}, "
            f"Version: {final_agg_ser_df_artifact.version}\n"
            f"2. Spaces dict - Name: {spaces_clean_name}, "
            f"Version: {spaces_clean_artifact.version}"
        )

    if training_pipeline:
        training.with_options(**pipeline_args)(
            final_agg_ser_df_version_id=final_agg_ser_df_version_id,
            spaces_clean_version_id=spaces_clean_version_id,
        )
        trained_models_artifact = client.get_artifact_version(trained_models_name)
        logger.info("Training pipeline finished successfully!")
        logger.info(
            f"Training pipeline produced:\n"
            f"Trained models - Name: {trained_models_name}, "
            f"Version: {trained_models_artifact.version}"
        )


if __name__ == "__main__":
    main()
