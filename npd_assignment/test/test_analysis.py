import pandas as pd
import pytest

from npd_assignment.analysis import Stats
from npd_assignment.exceptions import (
    EmptyIntervalException, MissingColumnsException
)


@pytest.fixture
def stats_df():
    return pd.DataFrame({
        "Country": ["POLAND", "BURKINA FASO", "CHINA", "ARUBA"],
        "Year": [2, 1, 3, 7],
        "GDP [current US$]": [2.0, 2.0, 2.0, 2.0],
        "Population": [2, 2, 2, 2],
        "Emissions [total metric tons]": [2.0, 2.0, 2.0, 2.0],
    })


class TestStats:

    def test_init(self):
        with pytest.raises(MissingColumnsException):
            tmp = Stats(pd.DataFrame({
                "COL1": [1, 2, 3],
                "Year": [3, 2, 1]
            }))

    def test_precompute_columns(self, stats_df):
        tmp = Stats(stats_df)
        tmp._precompute_columns()
        assert tmp.df[
                   "Emissions [metric tons per capita]"].tolist() == [1.0] * 4
        assert tmp.df["GDP [current US$ per capita]"].tolist() == [1.0] * 4

    def test_gdp_stats_per_year(self, stats_df):
        tmp = Stats(stats_df)
        with pytest.raises(EmptyIntervalException):
            _ = tmp.gdp_stats_per_year(year_range=(2000, 2010))

    def test_emission_stats_per_year(self, stats_df):
        tmp = Stats(stats_df)
        with pytest.raises(EmptyIntervalException):
            _ = tmp.emission_stats_per_year(year_range=(2000, 2010))

    def test_emission_change_stats(self, stats_df):
        tmp = Stats(stats_df)
        result = tmp.emission_change_stats()
        assert all(elt.empty for elt in result)



