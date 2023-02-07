import logging

import pandas as pd

from typing import Tuple, Optional

import utils
from config import CONFIG


class Stats:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.top_k = CONFIG["stats_top_k"]
        self._precompute_columns()

    def _precompute_columns(self) -> None:
        self.df["GDP [current US$ per capita]"] = self.df["GDP [current US$]"] / self.df["Population"]
        self.df["Emissions [metric tons per capita]"] = self.df["Emissions [total metric tons]"] / self.df["Population"]

    def gdp_stats_per_year(self, year_range: Tuple[Optional[int], Optional[int]] = (None, None)) -> pd.DataFrame:
        stats = self.df[["Year", "Country", "GDP [current US$]", "GDP [current US$ per capita]"]]

        lower, upper = year_range
        if lower:
            logging.info(f"Selecting years no earlier than {lower}...")
            stats.query("Year >= @lower", inplace=True)
        if upper:
            logging.info(f"Selecting years no later than {upper}...")
            stats.query("Year <= @upper", inplace=True)

        logging.info(f"Calculating {self.top_k} countries with largest GDP per capita for each year."
                     f"Please note: if a country has no available data for a given year, "
                     f"it will not be taken into consideration in computing the statistical table for that year.")
        stats_table = stats.groupby("Year")["GDP [current US$ per capita]"].nlargest(self.top_k).to_frame()
        stats_table.index.rename(["Year", "ID"], inplace=True)
        return stats_table.join(stats)[
            ["Country", "GDP [current US$]"]][
            ["Country", "GDP [current US$ per capita]", "GDP [current US$]"]]

    def emission_stats_per_year(self, year_range: Tuple[Optional[int], Optional[int]] = (None, None)) -> pd.DataFrame:
        stats = self.df[["Year", "Country", "Emissions [total metric tons]", "Emissions [metric tons per capita]"]]

        lower, upper = year_range
        if lower:
            logging.info(f"Selecting years no earlier than {lower}...")
            stats.query("Year >= @lower", inplace=True)
        if upper:
            logging.info(f"Selecting years no later than {upper}...")
            stats.query("Year <= @upper", inplace=True)

        logging.info(f"Calculating {self.top_k} countries with largest emissions per capita for each year."
                     f"Please note: if a country has no available data for a given year, "
                     f"it will not be taken into consideration in computing the statistical table for that year.")
        stats_table = stats.groupby("Year")["Emissions [total metric tons]"].nlargest(self.top_k).to_frame()
        stats_table.index.rename(["Year", "ID"], inplace=True)
        return stats_table.join(stats)[
            ["Country", "Emissions [total metric tons]"]][
            ["Country", "Emissions [total metric tons]", "Emissions [metric tons per capita]"]]

    def emission_change_stats(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        stats = self.df[["Year", "Country", "Emissions [metric tons per capita]"]]

        most_recent_year = stats["Year"].max()
        decade_ago = most_recent_year - 10
        if decade_ago not in stats["Year"]:
            logging.error(f"Cannot compute changes in CO2 emissions during most recent decade: "
                          f"no data corresponding to year {most_recent_year} - 10 = {decade_ago}.")
            return pd.DataFrame(), pd.DataFrame()

        utils.restrict_column(stats, "Year",  {most_recent_year, decade_ago})
        stats_recent, stats_ago = stats.query("Year == @most_recent_year"), stats.query("Year == @decade_ago")
        common_countries = utils.get_common_subset("Country", stats_recent, stats_ago)
        for df in (stats_recent. stats_recent, stats_ago):
            utils.restrict_column(df, "Country", common_countries)

        logging.info("Calculating countries with largest emission changes per capita during last decade available in data. "
                     "Please note: only countries with data available for both years (most recent and a decade before) "
                     "will be taken into consideration.")
        stats_ago.sort_values("Country", inplace=True)
        stats_recent.sort_values("Country", inplace=True)
        # delta > 0 means increase in emissions
        stats_recent["delta"] = \
            stats_recent["Emissions [metric tons per capita]"] - stats_ago["Emissions [metric tons per capita]"]
        top_increase = stats_recent.sort_values("delta", ascending=False)[["Country", "delta"]].rename({
            "delta": "Difference in emissions"
        }, axis=1).head(self.top_k)
        top_decrease = stats_recent.sort_values("delta", ascending=True)[["Country", "delta"]].rename({
            "delta": "Difference in emissions"
        }, axis=1).head(self.top_k)
        return top_increase, top_decrease
