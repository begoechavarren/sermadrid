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

Run the ZenML sermadrid pipelomes:

  \b
  # Run the feature engineering pipeline
    python run.py --feature-pipeline

  \b
  # Run the training pipeline
    python run.py --training-pipeline

  \b
  # Run the training pipeline with versioned artifacts
    python run.py --training-pipeline --train-dataset-version-name=1 --test-dataset-version-name=1

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
# @click.option(
#     "--test-dataset-name",
#     default="dataset_tst",
#     type=click.STRING,
#     help="The name of the test dataset produced by feature engineering.",
# )
# @click.option(
#     "--test-dataset-version-name",
#     default=None,
#     type=click.STRING,
#     help="Version of the test dataset produced by feature engineering. "
#     "If not specified, a new version will be created.",
# )
@click.option(
    "--feature-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the pipeline that creates the dataset.",
)
@click.option(
    "--training-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the pipeline that trains the model.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
def main(
    final_agg_ser_df_name: str = "tuned_ser_df",
    spaces_clean_name: str = "spaces_clean",
    trained_models_name: str = "trained_models",
    final_agg_ser_df_version_id: Optional[UUID] = None,
    spaces_clean_version_id: Optional[UUID] = None,
    feature_pipeline: bool = False,
    training_pipeline: bool = False,
    no_cache: bool = False,
):
    """Main entry point for the pipeline execution.

    This entrypoint is where everything comes together:

      * configuring pipeline with the required parameters
        (some of which may come from command line arguments, but most
        of which comes from the YAML config files)
      * launching the pipeline

    Args:
        final_agg_ser_df: The name of the dataset produced by feature engineering.
        train_dataset_version_name: Version of the train dataset produced by feature engineering.
            If not specified, a new version will be created.
        test_dataset_name: The name of the test dataset produced by feature engineering.
        test_dataset_version_name: Version of the test dataset produced by feature engineering.
            If not specified, a new version will be created.
        feature_pipeline: Whether to run the pipeline that creates the dataset.
        training_pipeline: Whether to run the pipeline that trains the model.
        inference_pipeline: Whether to run the pipeline that performs inference.
        no_cache: If `True` cache will be disabled.
    """
    print("ZenML version", zenml.__version__)
    client = Client()

    # config_folder = os.path.join(
    #     os.path.dirname(os.path.realpath(__file__)),
    #     "configs",
    # )

    # Execute Feature Engineering Pipeline
    if feature_pipeline:
        feature_engineering()
        logger.info("Feature Engineering pipeline finished successfully!\n")

        final_agg_ser_df_artifact = client.get_artifact_version(final_agg_ser_df_name)
        spaces_clean_artifact = client.get_artifact_version(spaces_clean_name)

        logger.info(
            "The latest feature engineering pipeline produced the following "
            f"artifact: \n\n1. SER dataset - Name: {final_agg_ser_df_name}, "
            f"Version Name: {final_agg_ser_df_artifact.version} \n2. Spaces dict: "
            f"Name: {spaces_clean_name}, Version Name: {spaces_clean_artifact.version}"
        )

    # Execute Training Pipeline
    if training_pipeline:
        # Run the RF pipeline
        # pipeline_args = {}
        # if no_cache:
        #     pipeline_args["enable_cache"] = False
        # pipeline_args["config_path"] = os.path.join(config_folder, "training_rf.yaml")
        # training.with_options(**pipeline_args)(**run_args_train)
        training(
            final_agg_ser_df_version_id=final_agg_ser_df_version_id,
            spaces_clean_version_id=spaces_clean_version_id,
        )
        trained_models_artifact = client.get_artifact_version(trained_models_name)
        logger.info("Training pipeline finished successfully!\n\n")
        logger.info(
            "The latest training pipeline produced the following "
            f"artifact: \n\n1. Trained models - Name: {trained_models_name}, "
            f"Version Name: {trained_models_artifact.version}"
        )


if __name__ == "__main__":
    main()
