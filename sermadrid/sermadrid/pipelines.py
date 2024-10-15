from typing import List

import numpy as np
import pandas as pd

from sermadrid.models import CustomProphetModelNH


# TODO: Move to backend?
class SerMadridInferencePipeline:
    def _inference(
        self,
        model: CustomProphetModelNH,
        datetime: pd.Timestamp | pd.DatetimeIndex,
    ) -> List[float]:
        if not isinstance(datetime, (pd.DatetimeIndex, list)):
            datetime = [datetime]

        predictions = model.inference(
            dates=datetime,
        )

        return predictions

    def run(
        self,
        datetime: pd.Timestamp | pd.DatetimeIndex,
        model: CustomProphetModelNH,
        num_plazas: int,
        return_percentage: bool = False,
    ) -> List[float]:
        predictions = self._inference(
            model=model,
            datetime=datetime,
        )

        if return_percentage:
            predictions = np.maximum(0, 1 - (predictions / num_plazas))

        return predictions
