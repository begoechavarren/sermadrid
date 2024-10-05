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
    # Convert `fecha_inicio` and `fecha_fin` to datetime
    ser_df = raw_ser_df.assign(
        fecha_inicio_dt=lambda df: pd.to_datetime(df["fecha_inicio"]),
        fecha_fin_dt=lambda df: pd.to_datetime(df["fecha_fin"]),
    )

    # Filter for valid data
    ser_df = ser_df[
        (ser_df["fecha_inicio_dt"].dt.year >= 2020)
        & (ser_df["fecha_inicio_dt"] < ser_df["fecha_fin_dt"])
    ]

    # Process `barrio` column
    neighbourhood_df = (
        ser_df[~ser_df["barrio"].str.contains(r"^\d", na=False)][
            ["barrio", "codigo_distrito", "codigo_barrio"]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
        .assign(
            codigo_distrito=lambda df: df["codigo_distrito"].astype(int),
            codigo_barrio=lambda df: df["codigo_barrio"].astype(int),
            barrio_id=lambda df: (
                df["codigo_distrito"].astype(str)
                + df["codigo_barrio"].apply(lambda x: f"{x:02}")
            ).astype(int),
            codigo_combinado=lambda df: df["codigo_distrito"].apply(lambda x: f"{x:02}")
            + "-"
            + df["codigo_barrio"].apply(lambda x: f"{x:02}"),
            barrio=lambda df: df["barrio"].apply(lambda x: unidecode(x.strip())),
        )
        .drop_duplicates()
        .reset_index(drop=True)
    )

    barrio_to_id_map = neighbourhood_df.set_index("barrio")["barrio_id"].to_dict()

    def clean_barrio(text):
        if text[0].isdigit():
            text = neighbourhood_df.loc[neighbourhood_df["codigo_combinado"] == text][
                "barrio"
            ].values[0]
        else:
            text = unidecode(text.strip())
        return text

    ser_df = ser_df.assign(
        barrio=lambda df: df["barrio"].progress_apply(clean_barrio),
        barrio_id=lambda df: df["barrio"].map(barrio_to_id_map),
    )

    # Fix specific `barrio` values and remove unwanted ones
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
        raw_spaces_df: The raw dataset to be processed.

    Returns:
        The processed dataset (spaces_grouped_df).
        The cleaned dict (spaces_clean).
    """
    logger.info(f"Processing spaces data with columns...{raw_spaces_df.columns}")
    # Create `barrio_id` and clean `barrio` names
    spaces_df = raw_spaces_df.assign(
        barrio_id=lambda df: df["barrio"]
        .str.extract(r"(\d{2})-(\d{2})")
        .agg("".join, axis=1)
        .astype(int),
        barrio=lambda df: df["barrio"].apply(
            lambda x: unidecode(" ".join(x.split()[1:]))
        ),
    )
    spaces_df.loc[spaces_df["barrio"] == "CARMENES", "barrio"] = "LOS CARMENES"

    # Pivot and aggregate data
    spaces_pivoted = (
        spaces_df.groupby(["barrio", "barrio_id", "color"])["num_plazas"]
        .sum()
        .reset_index()
        .pivot(index=["barrio", "barrio_id"], columns="color", values="num_plazas")
        .fillna(0)
        .reset_index()
        .rename(
            columns={
                "043000255 Azul": "num_plazas_azules",
                "077214010 Verde": "num_plazas_verdes",
            }
        )
        .assign(
            num_plazas_azules=lambda df: df["num_plazas_azules"].astype(int),
            num_plazas_verdes=lambda df: df["num_plazas_verdes"].astype(int),
            num_plazas=lambda df: df["num_plazas_azules"] + df["num_plazas_verdes"],
        )
    )

    # Create `spaces_grouped_df`` DataFrame
    spaces_grouped_df = spaces_pivoted[
        ["barrio", "barrio_id", "num_plazas", "num_plazas_azules", "num_plazas_verdes"]
    ]

    # Create `spaces_clean` dictionary
    spaces_dict = spaces_grouped_df.set_index("barrio_id").to_dict(orient="index")
    spaces_clean = {
        barrio_id: {
            "barrio": details["barrio"],
            "num_plazas": details["num_plazas_azules"] or details["num_plazas_verdes"],
        }
        for barrio_id, details in spaces_dict.items()
    }

    return spaces_grouped_df, spaces_clean
