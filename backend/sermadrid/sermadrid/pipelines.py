from typing import Dict, List

import pandas as pd

from sermadrid.models import CustomProphetModelNH


class SerMadridInferencePipeline:
    def _inference(
        self,
        model: CustomProphetModelNH,
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
        model,
        spaces_dict: Dict,
        barrio_id: str,
        return_percentage: bool = False,
    ):
        predictions = self._inference(
            model=model,
            datetime=datetime,
        )

        if return_percentage:
            num_plazas = spaces_dict[barrio_id]
            predictions = 1 - (predictions / num_plazas)

        return predictions
