import json
import os

import cloudpickle

models = {}
spaces_dict = {}


def load_data():
    global models, spaces_dict
    CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Load models
    model_dir = os.path.join(CURRENT_DIR, "app", "data", "models")
    for model_file in os.listdir(model_dir):
        if model_file.endswith(".pkl"):
            model_path = os.path.join(model_dir, model_file)
            with open(model_path, "rb") as f:
                models[model_file.split(".")[0]] = cloudpickle.load(f)

    # Load spaces data
    spaces_data_path = os.path.join(
        CURRENT_DIR, "app", "data", "input", "spaces_clean.json"
    )
    with open(spaces_data_path, "r") as json_file:
        spaces_clean = json.load(json_file)
        for key, value in spaces_clean.items():
            spaces_dict[key] = value


def get_models_and_spaces():
    return models, spaces_dict
