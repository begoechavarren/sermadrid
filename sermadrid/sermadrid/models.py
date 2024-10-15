import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_from_json, model_to_json
from workalendar.europe import CommunityofMadrid

import mlflow


class CustomProphetModelNH(mlflow.pyfunc.PythonModel):
    def __init__(self, barrio_id: int) -> None:
        self.model = None
        self.barrio_id = barrio_id
        super().__init__()

    def __str__(self) -> str:
        return "Custom Facebook Prophet"

    def _create_train_df(
        self, y_train: np.ndarray, agg_df: pd.DataFrame
    ) -> pd.DataFrame:
        X_train_datetime = agg_df.index[: len(y_train)]
        prophet_train_df = pd.DataFrame({"ds": X_train_datetime, "y": y_train})
        return prophet_train_df

    def _create_nh_agg_df(self, agg_df: pd.DataFrame) -> pd.DataFrame:
        agg_df_nh = agg_df[agg_df["barrio_id"] == self.barrio_id]
        return agg_df_nh

    def _build_model(self, **params) -> Prophet:
        custom_daily_fourier = params.pop("custom_daily_fourier", 8)
        self.model = Prophet(**params)
        self.model.add_seasonality(
            name="custom_daily", period=1, fourier_order=custom_daily_fourier
        )

    def train(
        self,
        X_train: np.ndarray = None,
        y_train: np.ndarray = None,
        agg_df: pd.DataFrame = None,
    ) -> None:
        # TODO: Implement hyperparameter tuning?
        params = {
            "changepoint_prior_scale": 0.001,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive",
            "yearly_seasonality": "auto",
            "weekly_seasonality": "auto",
            "daily_seasonality": True,
            "custom_daily_fourier": 8,
        }
        self._build_model(**params)
        nh_agg_df = self._create_nh_agg_df(agg_df)
        if y_train is None:
            y_train = nh_agg_df["active_tickets"].values
        prophet_train_df = self._create_train_df(y_train=y_train, agg_df=nh_agg_df)
        self.model.fit(prophet_train_df)

    def inference(self, dates: np.ndarray) -> np.ndarray:
        prophet_predict_df = pd.DataFrame({"ds": pd.to_datetime(dates)})
        forecast = self.model.predict(prophet_predict_df)

        forecast["on_sunday"] = (forecast.ds.dt.dayofweek == 6).astype(int)
        forecast["night"] = (
            (forecast.ds.dt.hour >= 21) | (forecast.ds.dt.hour < 9)
        ).astype(int)
        forecast["saturday_afternoon"] = (
            (forecast.ds.dt.dayofweek == 5)
            & (forecast.ds.dt.hour >= 15)
            & (forecast.ds.dt.hour < 21)
        ).astype(int)
        forecast["august_afternoon"] = (
            (forecast.ds.dt.month == 8)
            & (forecast.ds.dt.dayofweek < 5)
            & (forecast.ds.dt.hour >= 15)
            & (forecast.ds.dt.hour < 21)
        ).astype(int)
        madrid_holidays = CommunityofMadrid()
        forecast["madrid_holidays"] = forecast.ds.dt.date.apply(
            madrid_holidays.is_holiday
        ).astype(int)

        forecast.loc[forecast["on_sunday"] == 1, "yhat"] = 0
        forecast.loc[forecast["night"] == 1, "yhat"] = 0
        forecast.loc[forecast["saturday_afternoon"] == 1, "yhat"] = 0
        forecast.loc[forecast["august_afternoon"] == 1, "yhat"] = 0
        forecast.loc[forecast["madrid_holidays"] == 1, "yhat"] = 0

        y_pred_prophet = forecast["yhat"].values
        y_pred_prophet = np.where(y_pred_prophet < 0, 0, y_pred_prophet)
        return y_pred_prophet

    def __getstate__(self):
        state = self.__dict__.copy()
        if self.model:
            state["model_json"] = model_to_json(self.model)
            del state["model"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if "model_json" in state:
            self.model = model_from_json(state["model_json"])
        else:
            self.model = None

    def predict(self, context, model_input):
        return self.model.inference(dates=model_input)
