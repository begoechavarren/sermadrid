from unidecode import unidecode

from app.app.core.celery_app import app
from app.app.schemas.output import ParkingResult


@app.task
def predict_parking_availability(
    datetime_str: str, latitude_str: str, longitude_str: str
) -> ParkingResult:
    import os
    import random

    import cloudpickle
    import pandas as pd

    from app.app.schemas.input import DateTime, Location
    from sermadrid.models import CustomProphetModelNH
    from sermadrid.pipelines import SerMadridInferencePipeline

    CURRENT_DIR = os.path.dirname(__file__)
    SERMADRID_INFERENCE = SerMadridInferencePipeline()
    DATETIME_SINGLE = pd.to_datetime(datetime_str)
    # TODO: Calculate barrio_id from latitude and longitude
    BARRIO_ID = "405"
    MODEL_PATH = os.path.join(CURRENT_DIR, "data", "artifacts", "405.pkl")

    print(CustomProphetModelNH)
    with open(MODEL_PATH, "rb") as f:
        MODEL = cloudpickle.load(f)

    def load_spaces_data(path: str) -> pd.DataFrame:
        spaces_df = pd.read_csv(
            path,
            delimiter=";",
            encoding="ISO-8859-1",
            low_memory=False,
        )
        spaces_df["barrio_id"] = (
            spaces_df["barrio"]
            .str.extract(r"(\d{2})-(\d{2})")
            .apply(lambda x: x[0] + x[1], axis=1)
            .astype(int)
        )
        spaces_df["barrio"] = spaces_df["barrio"].apply(
            lambda x: unidecode(" ".join(x.split()[1:]))
        )
        spaces_df.loc[spaces_df["barrio"] == "CARMENES", "barrio"] = "LOS CARMENES"
        spaces_df = (
            spaces_df.groupby(["barrio", "barrio_id"])
            .agg({"num_plazas": "sum"})
            .reset_index()
        )
        return spaces_df

    SPACES_DATA_PATH = os.path.join(CURRENT_DIR, "data", "input", "spaces.csv")
    SPACES_DF = load_spaces_data(SPACES_DATA_PATH)

    datetime = DateTime(datetime=datetime_str)
    location = Location(latitude=latitude_str, longitude=longitude_str)
    print(f"Predicting parking availability for {datetime} at {location}")

    prediction = SERMADRID_INFERENCE.run(
        datetime=DATETIME_SINGLE,
        barrio_id=BARRIO_ID,
        model=MODEL,
        spaces_df=SPACES_DF,
        return_percentage=True,
    )[0]
    print(f"Predictions: {prediction}")
    result = random.choice(["easy", "medium", "hard"])
    return {
        "result": result,
        "prediction": prediction,
    }
