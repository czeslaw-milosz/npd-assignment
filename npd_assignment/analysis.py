import logging

import pandas as pd

from typing import Tuple, Optional


def gdp_stats_per_year(df: pd.DataFrame, k_max: int = 5,
                       year_range: Tuple[Optional[int], Optional[int]] = (None, None)) -> pd.DataFrame:
    stats = df[["Year", "Country", "GDP", "Population"]]

    lower, upper = year_range
    if lower:
        logging.info(f"Selecting years no earlier than {lower}...")
        stats.query("Year >= @lower", inplace=True)
    if upper:
        logging.info(f"Selecting years no later than {upper}...")
        stats.query("Year <= @upper", inplace=True)

    stats["GDP [current US$ per capita]"] = stats["GDP"] / stats["Population"]
    stats.rename({"GDP": "GDP [current US$]"}, axis=1, inplace=True)

    logging.info(f"Calculating {k_max} countries with largest GDP per capita for each year."
                 f"Please note: if a country has no available data for a given year, "
                 f"it will not be taken into consideration in computing the statistical table for that year.")
    stats_table = stats.groupby("Year")["GDP [current US$ per capita]"].nlargest(k_max).to_frame()
    stats_table.index.rename(["Year", "ID"], inplace=True)
    return stats_table.join(stats)[
        ["Country", "GDP [current US$]"]][
        ["Country", "GDP [current US$ per capita]", "GDP [current US$]"]]


def emission_stats_per_year(df: pd.DataFrame, k_max: int = 5,
                            year_range: Tuple[Optional[int], Optional[int]] = (None, None)) -> pd.DataFrame:
    stats = df[["Year", "Country", "Emissions (total)", "Population"]]

    lower, upper = year_range
    if lower:
        logging.info(f"Selecting years no earlier than {lower}...")
        stats.query("Year >= @lower", inplace=True)
    if upper:
        logging.info(f"Selecting years no later than {upper}...")
        stats.query("Year <= @upper", inplace=True)

    stats["Emissions [total metric tons]"] = stats["Emissions (total)"] * 1000
    stats.drop("Emissions (total)", axis=1, inplace=True)
    stats["Emissions [metric tons per capita]"] = stats["Emissions [total metric tons]"] / stats["Population"]

    logging.info(f"Calculating {k_max} countries with largest emissions per capita for each year."
                 f"Please note: if a country has no available data for a given year, "
                 f"it will not be taken into consideration in computing the statistical table for that year.")
    stats_table = stats.groupby("Year")["Emissions [total metric tons]"].nlargest(k_max).to_frame()
    stats_table.index.rename(["Year", "ID"], inplace=True)
    return stats_table.join(stats)[
        ["Country", "Emissions [total metric tons]"]][
        ["Country", "Emissions [total metric tons]", "Emissions [metric tons per capita]"]]
