import json
import os

import cloudpickle
from celery import Celery
from celery.signals import worker_process_init

app = Celery("app", broker="redis://redis:6379/0")

app.conf.update(
    result_backend="redis://redis:6379/0",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

app.autodiscover_tasks(["app.app.worker.v1.tasks"])

models = {}
spaces_dict = {}


def load_data():
    global models, spaces_dict
    CURRENT_DIR = os.path.dirname(__file__)

    # Load models
    model_dir = os.path.join(CURRENT_DIR, "..", "worker", "v1", "data", "artifacts")
    for model_file in os.listdir(model_dir):
        if model_file.endswith(".pkl"):
            model_path = os.path.join(model_dir, model_file)
            with open(model_path, "rb") as f:
                models[model_file.split(".")[0]] = cloudpickle.load(f)

    # Load spaces data
    spaces_data_path = os.path.join(
        CURRENT_DIR, "..", "worker", "v1", "data", "input", "spaces_clean.json"
    )
    with open(spaces_data_path, "r") as json_file:
        spaces_clean = json.load(json_file)
        for key, value in spaces_clean.items():
            spaces_dict[key] = value


@worker_process_init.connect
def on_worker_process_init(**kwargs):
    load_data()
