import pandas as pd
import pytest

from npd_assignment.data_management import DataManager


@pytest.fixture
def raw_data_paths():
    return ("./data/emission_raw.csv",
            "./data/gdp_raw.csv",
            "./data/population_raw.csv")


@pytest.fixture
def data_before_preprocessing():
    return (pd.read_csv("./data/emission_before_preprocessing.csv"),
            pd.read_csv("./data/gdp_before_preprocessing.csv"),
            pd.read_csv("./data/population_before_preprocessing.csv"))


@pytest.fixture
def data_preprocessed():
    return (pd.read_csv("./data/emission_preprocessed.csv"),
            pd.read_csv("./data/gdp_preprocessed.csv"),
            pd.read_csv("./data/population_preprocessed.csv"))


@pytest.fixture
def full_df():
    return pd.read_csv("./data/full_df.csv")


class TestDataManager:
    def test_init(self, raw_data_paths):
        dm = DataManager(*raw_data_paths)
        assert all((dm._emission_df is None,
                    dm._gdp_df is None,
                    dm._population_df is None,
                    dm.full_df is None))
        assert all(
            x == y for x, y in zip(
                (dm.emissions_path, dm.gdp_path, dm.population_path),
                raw_data_paths
            )
        )

    def test_read_data(self, raw_data_paths, data_before_preprocessing):
        dm = DataManager(*raw_data_paths)
        tmp = dm._read_data(*raw_data_paths)
        assert all(
            (x.equals(y)
             for x, y in zip(
                (tmp[0], tmp[1], tmp[2]),
                data_before_preprocessing))
        )

    def test_preprocess_data(self, raw_data_paths, data_preprocessed):
        dm = DataManager(*raw_data_paths)
        dm.load_data(preprocess=True)
        assert all(
            (x.equals(y)
             for x, y in zip(
                (dm._emission_df, dm._gdp_df, dm._population_df),
                data_preprocessed))
        )

    @pytest.mark.parametrize(
        ("data", "expected_year", "expected_country"),
        [
            ((pd.DataFrame({"Year": [1, 2], "Country": ["Poland", "China"]}),
             pd.DataFrame(
                 {"Year": [1, 6, 5], "Country": ["Poland", "ASDF", "ASDF"]}),
             pd.DataFrame({"Year": [3, 1], "Country": ["ASDF", "Poland"]})),
             [1, ], ["Poland", ]),
            ((pd.DataFrame({"Year": [1, 2], "Country": ["Poland", "China"]}),
              pd.DataFrame({"Year": [6, 5], "Country": ["ASDF", "ASDF"]}),
              pd.DataFrame({"Year": [3, 3], "Country": ["QWERTY", "QWERTY"]})),
             [], []),
        ]
    )
    def test_ensure_data_consistency(self, data, expected_year,
                                     expected_country):
        dm = DataManager("", "", "")
        dm._emission_df, dm._gdp_df, dm._population_df = data
        dm._ensure_data_consistency()
        assert all(
            df["Year"].tolist() == expected_year for df in (
                dm._emission_df, dm._gdp_df, dm._population_df
            )
        )
        assert all(
            df["Country"].tolist() == expected_country for df in (
                dm._emission_df, dm._gdp_df, dm._population_df
            )
        )

    def test_get_full_data(self, full_df, raw_data_paths):
        dm = DataManager(*raw_data_paths)
        dm.load_data()
        tmp = dm.get_full_data()
        assert dm.full_df is not None
        assert tmp.compare(full_df).empty
