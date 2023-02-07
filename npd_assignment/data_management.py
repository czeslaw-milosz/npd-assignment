import functools
import logging
from typing import Tuple

import pandas as pd

from npd_assignment import utils


class DataManager:

    def __init__(self, emissions_path: str, gdp_path: str, population_path: str) -> None:
        self.emissions_path = emissions_path
        self.gdp_path = gdp_path
        self.population_path = population_path

        self._emission_df, self._gdp_df, self._population_df = self._read_data(self.emissions_path,
                                                                               self.gdp_path,
                                                                               self.population_path)
        self.full_df = None
        self._preprocess_data()

    def get_full_data(self) -> pd.DataFrame:
        self._make_full_dataset()
        return self.full_df

    def _make_full_dataset(self) -> None:
        self.full_df = functools.reduce(
            lambda left, right: pd.merge(left, right, on=["Country", "Year"]),
            (self._emission_df,
             self._gdp_df.drop(["Country Code", "Indicator Name"], axis=1),
             self._population_df.drop(["Country Code", "Indicator Name"], axis=1))
        )
        self.full_df.index.rename("ID", inplace=True)

    def _preprocess_data(self):
        for df in (self._gdp_df, self._population_df):
            utils.remove_non_countries(df)
        utils.col_to_uppercase(self._emission_df, "Country")
        utils.col_to_uppercase(self._gdp_df, "Country")
        utils.col_to_uppercase(self._population_df, "Country")
        self._gdp_df = utils.reshape_worldbank_df(self._gdp_df, "GDP")
        self._population_df = utils.reshape_worldbank_df(self._population_df, "Population")
        for df in (self._emission_df, self._gdp_df, self._population_df):
            utils.standardize_country_names(df)
        self._ensure_data_consistency()
        self._emission_df["Emissions (total)"] *= 1000
        self._emission_df.rename({"Emissions (total)": "Emissions [total metric tons]"}, axis=1, inplace=True)
        self._gdp_df.rename({"GDP": "GDP [current US$]"}, axis=1, inplace=True)

    def _ensure_data_consistency(self) -> None:
        common_years = utils.get_common_subset("Year", self._emission_df, self._gdp_df, self._population_df)
        common_countries = utils.get_common_subset("Country", self._emission_df, self._gdp_df, self._population_df)

        if not all(timeline == common_years
                   for timeline in (set(df["Year"]) for df in (self._emission_df, self._gdp_df, self._population_df))):
            logging.warning(f"There were discrepancies in the range of years between datasets; "
                            f"selecting a common subset of years. {len(common_years)} common years available.")
            for df in (self._emission_df, self._gdp_df, self._population_df):
                utils.restrict_column(df, "Year", common_years)

        if not all(countries == common_countries
                   for countries in (set(df["Country"]) for df in (self._emission_df, self._gdp_df, self._population_df))):
            msg = f"There were discrepancies in the range of countries between datasets; " \
                  f"selecting a common subset of countries ({len(common_countries)} countries available)."
            logging.warning(f"There were discrepancies in the range of countries between datasets; "
                            f"selecting a common subset of countries ({len(common_countries)} countries available).")
            for df in (self._emission_df, self._gdp_df, self._population_df):
                utils.restrict_column(df, "Year", common_years)

    @staticmethod
    def _read_data(emissions_path: str, gdp_path: str, population_path: str) \
            -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        emission_df = pd.read_csv(emissions_path)[["Year", "Country", "Total"]].rename(
            {"Total": "Emissions (total)"}, axis=1)
        gdp_df = pd.read_csv(gdp_path, skiprows=3).drop(["Indicator Code"], axis=1).iloc[:, :-1].rename(
            {"Country Name": "Country"}, axis=1)
        population_df = pd.read_csv(population_path, skiprows=3).drop("Indicator Code", axis=1).iloc[:, :-1].rename(
            {"Country Name": "Country"}, axis=1)
        return emission_df, gdp_df, population_df
