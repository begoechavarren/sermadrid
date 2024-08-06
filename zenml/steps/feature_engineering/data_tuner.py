import pandas as pd
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import step
from zenml.logger import get_logger

tqdm.pandas(desc="Processing rows")

logger = get_logger(__name__)


@step
def data_tuner(
    agg_ser_df: pd.DataFrame,
    spaces_grouped_df: pd.DataFrame,
) -> Annotated[pd.DataFrame, "tuned_ser_df"]:
    """Data tuning step.

    This step processes the aggregated dataset and tunes it to prepare it for model training.

    Args:
        agg_ser_df: The aggregated dataset to be tuned.

    Returns:
        The tuned dataset (tuned_ser_df).
    """

    def _fix_active_tickets(row, spaces_grouped_df, max_active_tickets: dict):
        barrio_id = row.barrio_id
        hour = row.name.hour
        active_tickets = row.active_tickets

        barrio_data = spaces_grouped_df[spaces_grouped_df["barrio_id"] == barrio_id]
        if barrio_data.empty:
            return active_tickets  # Return original value if `barrio_id` not found

        num_plazas_verdes_barrio = barrio_data["num_plazas_verdes"].iloc[0]
        num_plazas_azules_barrio = barrio_data["num_plazas_azules"].iloc[0]

        if barrio_id not in [101, 102, 103, 104, 105, 106]:
            # Avoid division by zero
            if num_plazas_azules_barrio == 0:
                return active_tickets

            hourly_factor_initial = (
                -0.01084 * (num_plazas_verdes_barrio / num_plazas_azules_barrio)
            ) + 0.9

            hourly_factors = {
                9: hourly_factor_initial,
                10: hourly_factor_initial,
                11: hourly_factor_initial,
                12: hourly_factor_initial,
                13: hourly_factor_initial,
                14: hourly_factor_initial,
                15: hourly_factor_initial,
                16: hourly_factor_initial + 0.05,
                17: hourly_factor_initial + 0.15,
                18: hourly_factor_initial + 0.2,
                19: hourly_factor_initial + 0.25,
                20: hourly_factor_initial + 0.3,
            }

            factor = hourly_factors.get(hour, 1.0)

            return active_tickets * factor

        else:
            max_active_tickets_barrio = max_active_tickets[barrio_id]
            delta = num_plazas_verdes_barrio - max_active_tickets_barrio
            return active_tickets + delta

    # Create the new DataFrame and apply the `fix_active_tickets` function
    max_active_tickets = (
        agg_ser_df.groupby("barrio_id")["active_tickets"]
        .quantile(1)
        .sort_values(ascending=False)
        .to_dict()
    )
    tuned_ser_df = agg_ser_df.assign(
        active_tickets=lambda df: df.progress_apply(
            lambda row: _fix_active_tickets(row, spaces_grouped_df, max_active_tickets),
            axis=1,
        )
    )

    return tuned_ser_df
