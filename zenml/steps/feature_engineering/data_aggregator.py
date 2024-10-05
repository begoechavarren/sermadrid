import numpy as np
import pandas as pd
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import step
from zenml.logger import get_logger

tqdm.pandas(desc="Processing rows")

logger = get_logger(__name__)


@step
def data_aggregator(
    ser_df: pd.DataFrame,
) -> Annotated[pd.DataFrame, "agg_ser_df"]:
    """Data aggregator step.

    This step aggregates the processed dataset.

    Args:
        ser_df: The dataset to be aggregated.

    Returns:
        The aggregated dataset (agg_ser_df).
    """
    # Filter for parking tickets that start on one day and end on the next day and expand them
    ser_next_day_filtered_df = ser_df[
        np.not_equal(
            ser_df["fecha_inicio_dt"].dt.day.values,
            ser_df["fecha_fin_dt"].dt.day.values,
        )
    ]

    def process_parking_dates(row):
        start = row["fecha_inicio_dt"]
        end = row["fecha_fin_dt"]
        barrio_id = row["barrio_id"]
        tipo_zona = row["tipo_zona"]
        segments = []

        # Take into account Saturdays and August schedule
        no_parking_start_hour = 14 if start.month == 8 or start.dayofweek == 5 else 20

        no_parking_start = pd.Timestamp(
            year=start.year,
            month=start.month,
            day=start.day,
            hour=no_parking_start_hour,
            minute=59,
        )
        no_parking_end = pd.Timestamp(
            year=end.year, month=end.month, day=end.day, hour=9, minute=0
        )

        segments.append(
            {
                "fecha_inicio_dt": start,
                "fecha_fin_dt": no_parking_start,
                "barrio_id": barrio_id,
                "tipo_zona": tipo_zona,
            }
        )
        segments.append(
            {
                "fecha_inicio_dt": no_parking_end,
                "fecha_fin_dt": end,
                "barrio_id": barrio_id,
                "tipo_zona": tipo_zona,
            }
        )

        return segments

    expanded_rows = ser_next_day_filtered_df.progress_apply(
        process_parking_dates, axis=1
    )
    ser_expanded_df = pd.DataFrame(
        [item for sublist in expanded_rows for item in sublist]
    )

    # Concatenate the expanded DataFrame with the non-filtered DataFrame
    next_day_filtered_indices = ser_next_day_filtered_df.index
    ser_non_filtered_df = ser_df.loc[~ser_df.index.isin(next_day_filtered_indices)][
        ["fecha_inicio_dt", "fecha_fin_dt", "barrio_id", "tipo_zona"]
    ]

    pre_agg_ser_df = pd.concat(
        [ser_non_filtered_df, ser_expanded_df], ignore_index=True
    ).reset_index(drop=True)

    # Filter for parking tickets that are in the blue and green zones
    pre_agg_ser_df = pre_agg_ser_df[pre_agg_ser_df["tipo_zona"].isin(["AZUL", "VERDE"])]

    def create_barrio_agg_ser_df(df: pd.DataFrame) -> pd.DataFrame:
        start_times = df["fecha_inicio_dt"].dt.floor("h").value_counts().sort_index()

        end_times = (
            (df["fecha_fin_dt"] + pd.Timedelta(hours=1))
            .dt.floor("h")
            .value_counts()
            .sort_index()
        )
        time_changes = (start_times.subtract(end_times, fill_value=0)).cumsum()

        start_date = df["fecha_inicio_dt"].min().floor("h")
        end_date = (df["fecha_fin_dt"].max() + pd.Timedelta(hours=1)).floor("h")

        if pd.isnull(start_date) or pd.isnull(end_date):
            logger.error("Start or end date is NaT")
            raise ValueError("Start or end date is NaT. Please check your input data.")

        try:
            time_range = pd.date_range(
                start=start_date,
                end=end_date,
                freq="h",
            )
        except Exception as e:
            logger.error(f"Error creating time_range: {str(e)}")
            raise

        agg_ser_df = (
            time_changes.reindex(time_range, method="ffill")
            .fillna(0)
            .to_frame(name="active_tickets")
        )
        return agg_ser_df

    all_barrio_zona_dfs = []
    for tipo_zona in tqdm(pre_agg_ser_df["tipo_zona"].unique()):
        for barrio_id in tqdm(pre_agg_ser_df["barrio_id"].unique()):
            barrio_zona_df = pre_agg_ser_df[
                (pre_agg_ser_df["barrio_id"] == barrio_id)
                & (pre_agg_ser_df["tipo_zona"] == tipo_zona)
            ].reset_index(drop=True)

            if barrio_zona_df.empty:
                logger.info(
                    f"Skipping barrio_id {barrio_id} and tipo_zona {tipo_zona} as it has no data"
                )
                continue

            barrio_zona_agg_ser_df = create_barrio_agg_ser_df(barrio_zona_df).assign(
                barrio_id=barrio_id, tipo_zona=tipo_zona
            )
            all_barrio_zona_dfs.append(barrio_zona_agg_ser_df)

    agg_ser_df = pd.concat(all_barrio_zona_dfs).assign(
        active_tickets=lambda df: np.where(df.index.hour == 21, 0, df["active_tickets"])
    )

    agg_ser_df.loc[
        (agg_ser_df.index.hour == 15) & (agg_ser_df.index.dayofweek == 5),
        "active_tickets",
    ] = 0
    agg_ser_df.loc[
        (agg_ser_df.index.hour == 15)
        & (agg_ser_df.index.month == 8)
        & (agg_ser_df.index.dayofweek < 5),
        "active_tickets",
    ] = 0

    agg_ser_df = agg_ser_df[
        (
            agg_ser_df["barrio_id"].isin([101, 102, 103, 104, 105, 106])
            & (agg_ser_df["tipo_zona"] == "VERDE")
        )
        | (
            ~agg_ser_df["barrio_id"].isin([101, 102, 103, 104, 105, 106])
            & (agg_ser_df["tipo_zona"] == "AZUL")
        )
    ]

    return agg_ser_df
