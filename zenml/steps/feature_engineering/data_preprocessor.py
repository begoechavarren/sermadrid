from typing import Tuple

import pandas as pd
from tqdm import tqdm
from typing_extensions import Annotated
from unidecode import unidecode
from zenml import step
from zenml.logger import get_logger

tqdm.pandas(desc="Processing rows")

logger = get_logger(__name__)


@step
def parkings_data_preprocessor(
    raw_ser_df: pd.DataFrame,
) -> Annotated[pd.DataFrame, "ser_df"]:
    """Data preprocessor step.

    This step processes the raw dataset to prepare it for model training.

    Args:
        raw_ser_df: The raw dataset to be processed.

    Returns:
        The processed dataset (ser_df).
    """

    ser_df = raw_ser_df.copy()

    logger.info("Converting 'fecha_inicio' and 'fecha_fin' to datetime...")
    ser_df["fecha_inicio_dt"] = pd.to_datetime(ser_df["fecha_inicio"])
    ser_df["fecha_fin_dt"] = pd.to_datetime(ser_df["fecha_fin"])

    logger.info("Filtering for valid data...")
    ser_df = ser_df[ser_df["fecha_inicio_dt"].dt.year >= 2020]
    ser_df = ser_df[ser_df["fecha_inicio_dt"] < ser_df["fecha_fin_dt"]]

    logger.info("Fixing 'barrio' column...")
    barrio_non_number_df = ser_df[~ser_df["barrio"].str.contains(r"^\d", na=False)]
    barrio_non_number_df = (
        barrio_non_number_df[["barrio", "codigo_distrito", "codigo_barrio"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    barrio_non_number_df["codigo_distrito"] = barrio_non_number_df[
        "codigo_distrito"
    ].astype(int)
    barrio_non_number_df["codigo_barrio"] = barrio_non_number_df[
        "codigo_barrio"
    ].astype(int)
    barrio_non_number_df["barrio_id"] = (
        barrio_non_number_df["codigo_distrito"].astype(str)
        + barrio_non_number_df["codigo_barrio"].apply(lambda x: f"{x:02}")
    ).astype(int)
    barrio_non_number_df["codigo_combinado"] = (
        barrio_non_number_df["codigo_distrito"].apply(lambda x: f"{x:02}")
        + "-"
        + barrio_non_number_df["codigo_barrio"].apply(lambda x: f"{x:02}")
    )
    barrio_df = (
        barrio_non_number_df[["barrio", "barrio_id", "codigo_combinado"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    barrio_df["barrio"] = barrio_df["barrio"].apply(lambda x: unidecode(x.strip()))
    barrio_to_id_map = barrio_df.set_index("barrio")["barrio_id"].to_dict()

    def clean_barrio(text):
        if text[0].isdigit():
            text = barrio_df.loc[barrio_df["codigo_combinado"] == text][
                "barrio"
            ].values[0]
        else:
            text = unidecode(text.strip())
        return text

    ser_df["barrio"] = ser_df["barrio"].progress_apply(clean_barrio)
    ser_df["barrio_id"] = ser_df["barrio"].map(barrio_to_id_map)
    ser_df.loc[ser_df["barrio"] == "PILAR", "barrio"] = "EL PILAR"
    ser_df = ser_df[
        ~ser_df["barrio"].isin(["ELO MONITORIZACION 1", "TALLER DEVAS", "TEST PARKARE"])
    ]
    ser_df.reset_index(drop=True, inplace=True)

    return ser_df


@step
def spaces_data_preprocessor(
    raw_spaces_df: pd.DataFrame,
) -> Tuple[
    Annotated[pd.DataFrame, "spaces_grouped_df"],
    Annotated[dict, "spaces_clean"],
]:
    """Data preprocessor step.

    This step processes the raw dataset to prepare it for model training.

    Args:
        spaces_df: The raw dataset to be processed.

    Returns:
        The processed dataset (spaces_grouped_df).
        The cleaned dict (spaces_clean).
    """
    spaces_df = raw_spaces_df.copy()

    # Create spaces_grouped_df
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
    spaces_grouped_temp = (
        spaces_df.groupby(["barrio", "barrio_id", "color"])["num_plazas"]
        .sum()
        .reset_index()
    )
    spaces_pivoted = spaces_grouped_temp.pivot(
        index=["barrio", "barrio_id"], columns="color", values="num_plazas"
    ).reset_index()
    spaces_pivoted = spaces_pivoted.rename(
        columns={
            "043000255 Azul": "num_plazas_azules",
            "077214010 Verde": "num_plazas_verdes",
        }
    ).fillna(0)
    spaces_pivoted["num_plazas"] = (
        spaces_pivoted["num_plazas_azules"] + spaces_pivoted["num_plazas_verdes"]
    )
    for col in ["num_plazas", "num_plazas_azules", "num_plazas_verdes"]:
        spaces_pivoted[col] = spaces_pivoted[col].astype(int)
    spaces_grouped_df = spaces_pivoted[
        ["barrio", "barrio_id", "num_plazas", "num_plazas_azules", "num_plazas_verdes"]
    ]

    # Create spaces_clean
    spaces_dict = spaces_grouped_df.set_index("barrio_id").to_dict()

    def get_num_plazas(barrio_id):
        num_plazas_azules = spaces_dict["num_plazas_azules"][barrio_id]

        if num_plazas_azules == 0:
            return spaces_dict["num_plazas_verdes"][barrio_id]
        else:
            return num_plazas_azules

    spaces_clean = {}
    for barrio_id in spaces_dict["barrio"]:
        spaces_clean[barrio_id] = {
            "barrio": spaces_dict["barrio"][barrio_id],
            "num_plazas": get_num_plazas(barrio_id),
        }

    return spaces_grouped_df, spaces_clean
