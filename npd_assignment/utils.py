# pylint: disable=W0613:
"""Utility functions for use across modules; mostly DataFrame wrangling."""

import logging
from typing import Any, Dict, Iterable, List, Set, Tuple, Union

import pandas as pd

from npd_assignment.config import CONFIG


def col_to_uppercase(df: pd.DataFrame, col_name: str) -> None:
    """Convert values of specified string column to uppercase.

    :param df: pd.DataFrame containing the column to convert
    :param col_name: name of the converted column
    :return: None: uppercase conversion is done in-place.
    """
    assert (
        col_name in df.columns
        and pd.api.types.infer_dtype(df[col_name]) == "string"
    )
    df[col_name] = df[col_name].str.upper()


def get_common_subset(col_name: str, *args) -> Set[Any]:
    """Extract common values of the given column across multiple dataframes.

    :param col_name: name of the column to be considered.
    :param args: arbitrary number of pd.DataFrames,
    all containing the column `col_name`.
    :return: the common subset of `col_name` values across all dataframes.
    """
    return set.intersection(*(set(df[col_name]) for df in args))


def remove_non_countries(
    df: pd.DataFrame, non_countries: List[str] = CONFIG["non_countries"]
) -> None:
    """Remove rows where `Country Code` column has values in `non_countries`.

    :param df: pd.DataFrame to be processed.
    :param non_countries: list of 'illegal' values to be removed
    from the `Country Code` column.
    :return: None: removal is done in-place.
    """
    df.query("~(`Country Code` in @non_countries)", inplace=True)


def reshape_worldbank_df(df: pd.DataFrame, value_colname: str) -> pd.DataFrame:
    """Reshape a dataframe from wide to long format for compatibility
    with emission data and easier analysis.

    The reshaped dataframe is assumed to have only year columns except three
    (`Country Code`, `Country`, `Indicator Name`). Years are gathered in the
    newly added `Year` column; values per year are stored in new column
    with name specified as `value_colname`.

    :param df: pd.DataFrame to reshape.
    :param value_colname: name of the new column with values for each year.
    :return: pd.DataFrame: the input dataframe reshape from wide to long format
    """
    return pd.melt(
        df,
        id_vars=["Country Code", "Country", "Indicator Name"],
        var_name="Year",
        value_name=value_colname,
    ).astype({"Year": "int64"})


def standardize_country_names(
    df: pd.DataFrame,
    names_dict: Dict[str, str] = CONFIG["standardized_country_names"],
) -> None:
    """Replace values in column `Country` with their standardized counterparts.

    Standarization rules are specified in `names_dict`, which by default is the
    dict included in `config.CONFIG`.

    :param df: pd.DataFrame to be processed.
    :param names_dict: standardization dictionary: raw_form->standardized_form.
    :return: None: standardization is done in-place.
    """
    df["Country"].replace(names_dict, inplace=True)


def reindex_grouped_table(
    df: pd.DataFrame, index_names: Union[List[str], Tuple[str]]
) -> pd.DataFrame:
    """Reset the inner indexing level in a 2-level multiindexed pd.DataFrame.

    :param df: pd.DataFrame to be reindexed.
    :param index_names: new names to be assigned to multiindex levels.
    :return: pd.DataFrame: reindexed version of the input dataframe.
    """
    assert len(index_names) == 2
    df.index = pd.MultiIndex.from_arrays(
        [df.index.get_level_values(0), df.groupby(level=0).cumcount() + 1],
        names=index_names,
    )
    return df


def restrict_column(
    df: pd.DataFrame, col_name: str, allowed_values: Iterable[Any]
) -> None:
    """Retain only `allowed_values` in column `col_name`, dropping all others.

    :param df: pd.DataFrame to be modified.
    :param col_name: column to perform value filtering on.
    :param allowed_values: iterable of allowed values for the column.
    :return: None: removal of disallowed values is done in-place.
    """
    df.query(f"`{col_name}` in @allowed_values", inplace=True)


def restrict_to_years_range(
    df: pd.DataFrame, year_range: Iterable[int]
) -> None:
    """Restrict dataframe so that all values in `Year`col  lay in `year_range`.

    :param df: pd.DataFrame to restrict.
    :param year_range: two-element iterable specifying the lower and upper
    bounds of the range (inclusive).
    :return: None: restricting is done in-place.
    """
    lower, upper = year_range
    if lower:
        logging.info("Selecting years no earlier than %d...", lower)
        df.query("Year >= @lower", inplace=True)
    if upper:
        logging.info("Selecting years no later than %d...", upper)
        df.query("Year <= @upper", inplace=True)
