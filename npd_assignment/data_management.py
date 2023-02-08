"""Data loading, storage, preprocessing and merging."""

import functools
import logging
from typing import Tuple

import pandas as pd

from npd_assignment import utils


class DataManager:
    """Object responsible for data handling.

    Attributes:

    """
    def __init__(
        self, emissions_path: str, gdp_path: str, population_path: str
    ) -> None:
        """Initializes a DataManager.

        Note that no data is loaded or processed when calling this constructor.
        Dataset loading should be triggered explicitly by using `load_data()`
        with an already existing DataManager.

        :param emissions_path: path to .csv file containing CO2 emissions data.
        :param gdp_path: path to .csv file containing GDP data.
        :param population_path: path to .csv file containing population data.
        """
        self.emissions_path = emissions_path
        self.gdp_path = gdp_path
        self.population_path = population_path

        self._emission_df, self._gdp_df, self._population_df = [None] * 3
        self.full_df = None

    def load_data(self, preprocess: bool = True) -> None:
        """Loads emission, GDP and population datasets into DataManager.

        :param preprocess: bool: Whether to preprocess dataset after loading.
        :return: None: loaded datasets are stored internally bu the DataManager
        as private attributes (in pd.DataFrame format).
        """
        self._emission_df, self._gdp_df, self._population_df = self._read_data(
            self.emissions_path, self.gdp_path, self.population_path
        )
        if preprocess:
            self._preprocess_data()

    def get_full_data(self) -> pd.DataFrame:
        """Makes the DataManager create and return a complete dataset created
        by cleaning and merging the emissions, GDP and population data.

        Please note that only the common subset of countries and years across
        all three dataframes is retained in the complete dataset.

        :return: pd.DataFrame containing the merged dataset;
        resulting dataframe has the following columns:
        - `Country`: standardized country name in uppercase;
        - `Year`: year (int);
        - `Emissions [total metric tons]`: total CO2 emissions in metric tons;
        (note that this is a different scale than in the original data);
        - `GDP [current US$]`: total GDP expressed in US dollars (float);
        - `Population`: total population (int).
        """
        self._make_full_dataset()
        return self.full_df

    def _make_full_dataset(self) -> None:
        """Internal method to create a clean, merged dataset (CO2 + GDP + Pop.)

        Emission, GDP and Population dataframes are merged on standardized
        country name and year; the method assumes that values in `Country` and
        `Year` columns are already the same between datasets (inner join
        is used). Index of the resulting dataframe is named `ID`.

        :return: None: the resulting merged emission+GDP+population dataframe
        is stored in DataManager's `full_df` attribute.
        """
        self.full_df = functools.reduce(
            lambda left, right: pd.merge(left, right, on=["Country", "Year"]),
            (
                self._emission_df,
                self._gdp_df.drop(["Country Code", "Indicator Name"], axis=1),
                self._population_df.drop(
                    ["Country Code", "Indicator Name"], axis=1
                ),
            ),
        )
        self.full_df.index.rename("ID", inplace=True)

    def _preprocess_data(self):
        """Internal method to perform data preprocessing.

        During preprocessing, the following operations are performed:
        - All rows corresponding to non-countries (as per `config.CONFIG`)
        are removed.
        - `Country` column is converted to uppercase in all dataframes.
        - GDP and population dataframes are reshaped from wide to long format
        for compatibility with emission data and easier analysis.
        -Uppercase country names are standardized using rules in config.CONFIG.
        - Data consistency is ensured: only the common subset of years and
        countries across the three dataframes is retained!
        - Emissions are rescaled to metric tons.
        - Columns are renamed to comply with config.CONFIG naming requirements.

        :return: None: preprocessing is performed in place on data stored by
        the DataManager.
        """
        for df in (self._gdp_df, self._population_df):
            utils.remove_non_countries(df)
        utils.col_to_uppercase(self._emission_df, "Country")
        utils.col_to_uppercase(self._gdp_df, "Country")
        utils.col_to_uppercase(self._population_df, "Country")
        self._gdp_df = utils.reshape_worldbank_df(self._gdp_df, "GDP")
        self._population_df = utils.reshape_worldbank_df(
            self._population_df, "Population"
        )
        for df in (self._emission_df, self._gdp_df, self._population_df):
            utils.standardize_country_names(df)
        self._ensure_data_consistency()
        self._emission_df["Emissions (total)"] *= 1000
        self._emission_df.rename(
            {"Emissions (total)": "Emissions [total metric tons]"},
            axis=1,
            inplace=True,
        )
        self._gdp_df.rename({"GDP": "GDP [current US$]"}, axis=1, inplace=True)

    def _ensure_data_consistency(self) -> None:
        """Ensures consistency in `Year` and `Country` cols across dataframes.

        Only the years and countries present in all three dataframes are
        retained. Note that this may potentially lead to significant data loss
        in case the datasets are poorly matching. If any rows are dropped,
        an appropriate warning is logged.

        :return: None: operation is performed in-place on data stored
        by the DataManager.
        """
        common_years = utils.get_common_subset(
            "Year", self._emission_df, self._gdp_df, self._population_df
        )
        common_countries = utils.get_common_subset(
            "Country", self._emission_df, self._gdp_df, self._population_df
        )

        if not all(
            timeline == common_years
            for timeline in (
                set(df["Year"])
                for df in (
                    self._emission_df,
                    self._gdp_df,
                    self._population_df,
                )
            )
        ):
            logging.warning(
                "There were discrepancies in the range of years "
                "between datasets; selecting a common subset of years "
                "(%d common years available).",
                len(common_years),
            )
            for df in (self._emission_df, self._gdp_df, self._population_df):
                utils.restrict_column(df, "Year", common_years)

        if not all(
            countries == common_countries
            for countries in (
                set(df["Country"])
                for df in (
                    self._emission_df,
                    self._gdp_df,
                    self._population_df,
                )
            )
        ):
            logging.warning(
                "There were discrepancies in the range of countries "
                "between datasets; selecting a common subset of countries "
                "(%d countries available).",
                len(common_countries),
            )
            for df in (self._emission_df, self._gdp_df, self._population_df):
                utils.restrict_column(df, "Year", common_years)

    @staticmethod
    def _read_data(
        emissions_path: str, gdp_path: str, population_path: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Internal method: read the raw emission, GDP & population data.

        :param emissions_path: path to .csv file containing CO2 emissions data.
        :param gdp_path: path to .csv file containing GDP data.
        :param population_path: path to .csv file containing population data.
        :return: None: Dataframes are read from the specified paths
        and stored in private attributes of the DataManager.
        """
        emission_df = pd.read_csv(emissions_path)[
            ["Year", "Country", "Total"]
        ].rename({"Total": "Emissions (total)"}, axis=1)
        gdp_df = (
            pd.read_csv(gdp_path, skiprows=3)
            .drop(["Indicator Code"], axis=1)
            .iloc[:, :-1]
            .rename({"Country Name": "Country"}, axis=1)
        )
        population_df = (
            pd.read_csv(population_path, skiprows=3)
            .drop("Indicator Code", axis=1)
            .iloc[:, :-1]
            .rename({"Country Name": "Country"}, axis=1)
        )
        return emission_df, gdp_df, population_df
