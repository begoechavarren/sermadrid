import os
from typing import List
from unidecode import unidecode
import pandas as pd
import joblib


class SerMadridInferencePipeline:
    def __init__(
        self,
        artifacts_path: str,
        spaces_path: str,
    ) -> None:
        self.artifacts_path = artifacts_path
        self.spaces_path = spaces_path

    def _load_model(
        self,
        barrio_id: str,
    ) -> None:
        model_path = os.path.join(self.artifacts_path, f"{barrio_id}.joblib")
        model = joblib.load(model_path)

        return model

    def _load_spaces_data(
        self,
    ) -> pd.DataFrame:
        csv_files = [
            file for file in os.listdir(self.spaces_path) if file.endswith(".csv")
        ]
        if len(csv_files) != 1:
            raise ValueError("There should be only one file in the spaces directory")
        spaces_df = pd.read_csv(
            os.path.join(self.spaces_path, csv_files[0]),
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

    def _inference(
        self,
        model,
        datetime: pd.Timestamp | pd.DatetimeIndex,
    ) -> List[float]:
        if not isinstance(datetime, (pd.DatetimeIndex, list)):
            datetime = [datetime]

        predictions = model.predict(
            dates=datetime,
        )

        return predictions

    def run(
        self,
        datetime: pd.Timestamp | pd.DatetimeIndex,
        barrio_id: str,
        return_percentage: bool = False,
    ):
        model = self._load_model(
            barrio_id=barrio_id,
        )
        predictions = self._inference(
            model=model,
            datetime=datetime,
        )

        if return_percentage:
            spaces_df = self._load_spaces_data()
            num_plazas = spaces_df[spaces_df["barrio_id"] == int(barrio_id)][
                "num_plazas"
            ].values[0]
            predictions = predictions / num_plazas

        return predictions
