# import json
# import os

# import cloudpickle

# models = {}
# spaces_dict = {}


# def load_data():
#     global models, spaces_dict
#     CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

#     # Load models
#     model_dir = os.path.join(CURRENT_DIR, "app", "data", "models")
#     for model_file in os.listdir(model_dir):
#         if model_file.endswith(".pkl"):
#             model_path = os.path.join(model_dir, model_file)
#             with open(model_path, "rb") as f:
#                 models[model_file.split(".")[0]] = cloudpickle.load(f)

#     # Load spaces data
#     spaces_data_path = os.path.join(
#         CURRENT_DIR, "app", "data", "input", "spaces_clean.json"
#     )
#     with open(spaces_data_path, "r") as json_file:
#         spaces_clean = json.load(json_file)
#         for key, value in spaces_clean.items():
#             spaces_dict[key] = value


# def get_models_and_spaces():
#     return models, spaces_dict

# TODO: Uncomment this code to use MLflow
import json
import os

import mlflow
from mlflow.tracking import MlflowClient

models = {}
spaces_dict = {}


def load_data():
    global models, spaces_dict

    # Set up MLflow client
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    client = MlflowClient()

    # Load models
    for model_name in client.search_registered_models():
        # Get the version with the 'champion' alias
        champion_version = client.get_model_version_by_alias(
            model_name.name, "champion"
        )
        if champion_version:
            models[model_name.name] = mlflow.pyfunc.load_model(
                f"models:/{model_name.name}@champion"
            ).unwrap_python_model()

    # Load spaces data
    spaces_run = client.search_runs(
        experiment_ids=[client.get_experiment_by_name("model_promotion").experiment_id],
        filter_string="tags.spaces_clean_production = 'true'",
        max_results=1,
        order_by=["attribute.start_time DESC"],
    )[0]

    spaces_artifact_path = client.download_artifacts(
        spaces_run.info.run_id, "spaces_clean/spaces_clean.json"
    )
    with open(spaces_artifact_path, "r") as json_file:
        spaces_dict = json.load(json_file)


def get_models_and_spaces():
    return models, spaces_dict
