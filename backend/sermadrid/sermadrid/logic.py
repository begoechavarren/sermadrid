from sermadrid.pipelines import SerMadridInferencePipeline
import pandas as pd

sermadrid_inference = SerMadridInferencePipeline(
    artifacts_path="artifacts",
    spaces_path="data/spaces",
)

# Example datetime for single prediction
DATETIME_SINGLE = pd.to_datetime("2024-08-16 11:00:00")
BARRIO_ID = "405"

predictions = sermadrid_inference.run(
    datetime=DATETIME_SINGLE,
    barrio_id=BARRIO_ID,
    return_percentage=True,
)
