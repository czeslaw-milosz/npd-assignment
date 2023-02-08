"""Analysis/basic statistical tables based on CO2, GDP and population data."""

import logging
from typing import Tuple, Optional

import pandas as pd

from npd_assignment import utils
from npd_assignment.config import CONFIG
from npd_assignment.exceptions import (
    EmptyIntervalException,
    MissingColumnsException,
)


class Stats:
    """Object responsible for computing statistic and summaries of the data."""
    def __init__(self, df: pd.DataFrame, top_k: int = CONFIG["stats_top_k"]
                 ) -> None:
        """Initialize a Stats object with a pre-prepared dataset.

        Note that the dataset provided as argument to __init__ must already be
        cleaned and preprocessed in a particular way. The best way to obtain
        a proper dataset is to use the output of `DataManager.get_full_data()`.
        In particular, the dataset must have the columns specified in
        `config.CONFIG['stats_required_columns'].

        :param df: pd.DataFrame to be analyzed. The dataframe is stored in
        `Stats.df` attribute after basic validtion.
        :param top_k: int specifying how many countries per level of grouping
        variable to return in the analyses; default specified by config.CONFIG.
        :raise MissingColumnException: if the dataset does not contain all the
        required columns as specified in `config.CONFIG`.
        """
        self.df = df
        self.top_k = top_k
        try:
            assert all(
                col_name in self.df.columns
                for col_name in CONFIG["stats_required_columns"]
            )
        except AssertionError as e:
            raise MissingColumnsException() from e
        self._precompute_columns()

    def gdp_stats_per_year(
        self, year_range: Tuple[Optional[int], Optional[int]] = (None, None)
    ) -> pd.DataFrame:
        """Find k countries with top GDP per each year present in the data."

        k is specified by the value of Stats.top_k attribute. The results are
        returned as a multi-indexed dataframe with two levels of index:
        `Year` and `ID`, where `ID` is simply row count per group.

        :param year_range: optionally, before computing the statistical table,
        years can be narrowed down to the year range.
        :return: pd.DataFrame: double-indexed table containing the results.
        :raise EmptyIntervalException: if no data is left
        after year range narrowing.
        """
        stats = self.df[
            [
                "Year",
                "Country",
                "GDP [current US$]",
                "GDP [current US$ per capita]",
            ]
        ]
        if any(year_range):
            utils.restrict_to_years_range(stats, year_range)
        # if no data is left after year restriction, raise an exception
        if stats.empty:
            raise EmptyIntervalException(year_range)

        logging.info(
            "Calculating %d countries with largest GDP per capita "
            "for each year. Please note: if a country has no available data "
            "for a given year, it will not be taken into consideration "
            "in computing the statistical table for that year.",
            self.top_k,
        )
        stats_table = (
            stats.groupby("Year")["GDP [current US$ per capita]"]
            .nlargest(self.top_k)
            .to_frame()
        )
        stats_table.index.rename(["Year", "ID"], inplace=True)
        return stats_table.join(stats[["Country", "GDP [current US$]"]])[
            ["Country", "GDP [current US$ per capita]", "GDP [current US$]"]
        ]

    def emission_stats_per_year(
        self, year_range: Tuple[Optional[int], Optional[int]] = (None, None)
    ) -> pd.DataFrame:
        """Find k countries with top CO2 emissions per each year present
        in the data."

        k is specified by the value of Stats.top_k attribute. The results are
        returned as a multi-indexed dataframe with two levels of index:
        `Year` and `ID`, where `ID` is simply row count per group.

        :param year_range: optionally, before computing the statistical table,
        years can be narrowed down to the year range.
        :return: pd.DataFrame: double-indexed table containing the results.
        :raise EmptyIntervalException: if no data is left after
        year range narrowing.
        """
        stats = self.df[
            [
                "Year",
                "Country",
                "Emissions [total metric tons]",
                "Emissions [metric tons per capita]",
            ]
        ]
        if any(year_range):
            utils.restrict_to_years_range(stats, year_range)
        if stats.empty:
            raise EmptyIntervalException(year_range)

        logging.info(
            "Calculating %d countries with largest emissions "
            "per capita for each year. Please note: if a country has no "
            "available data for a given year, it will not be taken into "
            "consideration in computing the statistical table for that year.",
            self.top_k,
        )
        stats_table = (
            stats.groupby("Year")["Emissions [metric tons per capita]"]
            .nlargest(self.top_k)
            .to_frame()
        )
        stats_table.index.rename(["Year", "ID"], inplace=True)
        return stats_table.join(
            stats[["Country", "Emissions [total metric tons]"]]
        )[
            [
                "Country",
                "Emissions [total metric tons]",
                "Emissions [metric tons per capita]",
            ]
        ]

    def emission_change_stats(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Find k countries with largest CO2 emission increase/decrease
         during last decade available in the data."

        k is specified by the value of Stats.top_k attribute. The results are
        returned as two ataframes for top increase and decrease. Note that
        positive values in the `Difference in CO2 emissions` column indicate
        emission increase relative to 10 years before the most recent year
        in the data, and negative values indicate emisison decrease.

        :return: two pd.DataFrames containing, respectively, the results
        for top emission increases and decreases. If the dataset does not
        contain emission data for last decade, `(None, None)` is returned.
        """
        stats = self.df[
            ["Year", "Country", "Emissions [metric tons per capita]"]
        ]

        most_recent_year = stats["Year"].max()
        decade_ago = most_recent_year - 10
        if decade_ago not in stats["Year"]:
            logging.error(
                "Cannot compute changes in CO2 emissions during "
                "most recent decade: no data corresponding to "
                "year %d - 10 = %d.",
                most_recent_year,
                decade_ago,
            )
            return pd.DataFrame(), pd.DataFrame()

        utils.restrict_column(stats, "Year", {most_recent_year, decade_ago})
        stats_recent, stats_ago = stats.query(
            "Year == @most_recent_year"
        ), stats.query("Year == @decade_ago")
        common_countries = utils.get_common_subset(
            "Country", stats_recent, stats_ago
        )
        for df in (stats_recent, stats_ago):
            utils.restrict_column(df, "Country", common_countries)

        logging.info(
            "Calculating countries with largest emission changes per capita"
            " during last decade of available data. Please note: only "
            "countries with data available for both years (most recent "
            "and a decade before) will be taken into consideration."
        )
        stats_ago.sort_values("Country", inplace=True, na_position="last")
        stats_recent.sort_values("Country", inplace=True)
        # delta > 0 means increase in emissions
        stats_recent["delta"] = (
            stats_recent["Emissions [metric tons per capita]"].values
            - stats_ago["Emissions [metric tons per capita]"].values
        )
        top_increase = (
            stats_recent.sort_values("delta", ascending=False)[
                ["Country", "delta"]
            ]
            .rename(
                {
                    "delta": f"Difference in CO2 emissions "
                    f"[metric tons per capita] -- "
                    f"top {self.top_k} increase across decade"
                },
                axis=1,
            )
            .head(self.top_k)
        )
        top_decrease = (
            stats_recent.sort_values("delta", ascending=True)[
                ["Country", "delta"]
            ]
            .rename(
                {
                    "delta": f"Difference in CO2 emissions "
                    f"[metric tons per capita] -- top "
                    f"{self.top_k} decrease across decade"
                },
                axis=1,
            )
            .head(self.top_k)
        )
        return top_increase, top_decrease

    def _precompute_columns(self) -> None:
        """Compute GDP and CO2 emisisons per capita from self.df dataframe.

        The following columns must be present in the dataframe:
        - `Population`
        - `GDP [current US$]`
        - `Emissions [total metric tons]`

        The following columns are computed (names should be self-explanatory):
        - `GDP [current US$ per capita]`
        - `Emissions [metric tons per capita]

        :return: None: new columns are added to self.df.
        """
        self.df["GDP [current US$ per capita]"] = (
            self.df["GDP [current US$]"] / self.df["Population"]
        )
        self.df["Emissions [metric tons per capita]"] = (
            self.df["Emissions [total metric tons]"] / self.df["Population"]
        )
