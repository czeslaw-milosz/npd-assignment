import pandas as pd
import pytest

from npd_assignment import utils
from npd_assignment.config import CONFIG


@pytest.fixture
def empty_df():
    return pd.DataFrame()


@pytest.fixture
def gdp_df():
    return pd.DataFrame(
        {
            "Country": ["POLAND", "BURKINA FASO", "CHINA", "ASDF"],
            "Year": [2, 1, 3, 7],
            "GDP [current US$]": [1.0, 1.5, 1.0, 0.0],
            "Indicator Name": ["GDP (current US$)"] * 4,
        }
    )


@pytest.fixture
def emission_df():
    return pd.DataFrame(
        {
            "Country": ["POLAND", "BURKINA FASO", "CHINA", "ASDF"],
            "Year": [2, 2, 3, 7],
            "Emissions [total metric tons]": [1.0, 1.5, 1.0, 0.0],
        }
    )


@pytest.fixture
def population_df():
    return pd.DataFrame(
        {
            "Country": ["POLAND", "BURKINA FASO", "CHINA", "ASDF"],
            "Country Code": ["PL", "BF", "CH", "TEA"],
            "Year": [2, 1, 3, 7],
            "Population": [7, 3, 1, 2],
            "Indicator Name": ["Population, total"] * 4,
        }
    )


@pytest.fixture
def worldbank_format_df():
    return pd.DataFrame(
        {
            "Country Code": ["A", "S", "D"],
            "Country": ["A", "S", "D"],
            "Indicator Name": ["ASDF"] * 3,
            "2000": [2000] * 3,
            "2001": [2001] * 3,
            "2002": [2002] * 3,
        }
    )


class TestColToUpperCase:
    @pytest.mark.parametrize(
        (
                "col_name",
                "dataframes",
        ),
        [
            (
                    "B",
                    (
                            pd.DataFrame(
                                {"A": [1, 2, 3], "B": ["a", "s", "d"]}),
                            pd.DataFrame(
                                {"C": [1, 2, 3], "B": ["a", "s", "d"]}),
                    ),
            ),
        ],
    )
    def test_col_to_uppercase(self, col_name, dataframes):
        for df in dataframes:
            utils.col_to_uppercase(df, col_name)
        assert all((s.isupper() for df in dataframes for s in df[col_name]))

    @pytest.mark.parametrize(
        ("col_name", "df"),
        [
            ("A", pd.DataFrame({"A": [1, 2, 3], "B": ["a", "s", "d"]})),
            (
                    "MISSING_COLUMN",
                    pd.DataFrame({"A": [1, 2, 3], "B": ["a", "s", "d"]}),
            ),
        ],
    )
    def test_col_to_uppercase_failure(self, col_name, df):
        with pytest.raises(AssertionError):
            utils.col_to_uppercase(df, col_name)


class TestGetCommonSubset:
    def test_get_common_subset(self, gdp_df, emission_df):
        common = utils.get_common_subset("Year", gdp_df, emission_df)
        assert common == {2, 3, 7}

    def test_get_common_subset_empty(self, gdp_df, population_df):
        assert (len(
            utils.get_common_subset("Indicator Name", gdp_df, population_df)
        ) == 0)


class TestRemoveNonCountries:
    @pytest.mark.parametrize(
        ("df", "expected_nrows"),
        [
            (pd.DataFrame({"Country Code": ["PL", "USA", "IT"]}), 3),
            (pd.DataFrame({"Country Code": ["PL", "USA", "TEA"]}), 2),
        ],
    )
    def test_remove_non_countries(self, df, expected_nrows):
        utils.remove_non_countries(df)
        assert df.shape[0] == expected_nrows
        if df.shape[0] == 2:
            assert "TEA" not in df["Country Code"]


class TestReshapeWorldbankDf:
    def test_reshape_worldbank_df(self, worldbank_format_df):
        tmp = utils.reshape_worldbank_df(worldbank_format_df, "ASDF")
        assert tmp.shape == (9, 5)
        assert "ASDF" in tmp.columns and "Year" in tmp.columns


class TestStandardizeCountryNames:
    def test_standardize_country_names(self):
        tmp = pd.DataFrame(
            {
                "Country": [
                    name for name in CONFIG["standardized_country_names"]
                ]
            }
        )
        utils.standardize_country_names(tmp)
        assert all(
            x == y
            for x, y in zip(
                tmp["Country"].values,
                CONFIG["standardized_country_names"].values(),
            )
        )


class TestRestrictColumn:
    def test_restrict_column(self, gdp_df, emission_df):
        utils.restrict_column(gdp_df, "Year", [2])
        assert gdp_df.shape[0] == 1
        utils.restrict_column(emission_df, "Year", [9, 8, 5])
        assert emission_df.empty


class TestRestrictToYearsRange:
    @pytest.mark.parametrize(
        ("df", "year_range", "expected"),
        [
            (pd.DataFrame({"Year": [1, 2, 3, 4]}), (2, 3), [2, 3]),
            (pd.DataFrame({"Year": [1, 2, 3, 4]}), (2, None), [2, 3, 4]),
            (pd.DataFrame({"Year": [1, 2, 3, 4]}), (None, 3), [1, 2, 3]),
            (pd.DataFrame({"Year": [1, 2, 3, 4]}), (None, None), [1, 2, 3, 4]),
        ],
    )
    def test_restrict_column(self, df, year_range, expected):
        utils.restrict_to_years_range(df, year_range)
        assert df["Year"].tolist() == expected
