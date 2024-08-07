import pandas as pd


def standardize_parking_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the column names of the parkings DataFrame.

    Args:
        df: The DataFrame to standardize.
    """
    df.columns = df.columns.str.strip()
    replacements = {
        "cod_distrito": "codigo_distrito",
        "cod_barrio": "codigo_barrio",
    }
    df.rename(columns=replacements, inplace=True)
    return df
