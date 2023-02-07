import logging
from typing import Any, Dict, Iterable, List, Set

import pandas as pd

from npd_assignment.config import CONFIG


def col_to_uppercase(df: pd.DataFrame, col_name: str) -> None:
    assert col_name in df.columns and pd.api.types.infer_dtype(df[col_name]) == "string"
    df[col_name] = df[col_name].str.upper()


def get_common_subset(col_name: str, *args) -> Set[Any]:
    return set.intersection(
        *(set(df[col_name]) for df in args)
    )


def remove_non_countries(df: pd.DataFrame, non_countries: List[str] = CONFIG["non_countries"]) -> None:
    df.query("~(`Country Code` in @non_countries)", inplace=True)


def reshape_worldbank_df(df: pd.DataFrame, value_colname: str) -> pd.DataFrame:
    return pd.melt(
        df,
        id_vars=["Country Code", "Country", "Indicator Name"],
        var_name="Year",
        value_name=value_colname
    ).astype({"Year": "int64"})


def standardize_country_names(df: pd.DataFrame, names_dict: Dict[str, str] = CONFIG["standardized_country_names"])\
        -> None:
    df["Country"].replace(names_dict, inplace=True)


def restrict_column(df: pd.DataFrame, col_name: str, allowed_values: Iterable[Any]) -> None:
    df.query(f"`{col_name}` in @allowed_values", inplace=True)


def restrict_to_years_range(df: pd.DataFrame, year_range: Iterable[int]) -> None:
    lower, upper = year_range
    if lower:
        logging.info(f"Selecting years no earlier than {lower}...")
        df.query("Year >= @lower", inplace=True)
    if upper:
        logging.info(f"Selecting years no later than {upper}...")
        df.query("Year <= @upper", inplace=True)
