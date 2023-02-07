import argparse
import logging

import tabulate

from .analysis import Stats
from .data_management import DataManager
from .exceptions import EmptyIntervalException

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--emissions_file",
        type=str,
        required=True,
        help="Path to .csv file containing the CO2 emissions data.",
    )
    parser.add_argument(
        "-g",
        "--gdp_file",
        type=str,
        required=True,
        help="Path to .csv file containing the GDP data.",
    )
    parser.add_argument(
        "-p",
        "--population_file",
        type=str,
        required=True,
        help="Path to .csv file containing the population data.",
    )
    parser.add_argument(
        "-start",
        type=int,
        required=False,
        help="Beginning of the requested time interval [in years]. Will be used to filter the data.",
    )
    parser.add_argument(
        "-koniec",
        type=int,
        required=False,
        help="Beginning of the requested time interval [in years]. Will be used to filter the data.",
    )

    args = parser.parse_args()

    emissions_path = args["emissions_file"]
    gdp_path = args["gdp_file"]
    population_path = args["population_file"]
    lower = args["start"] if "start" in args else None
    upper = args["start"] if "start" in args else None
    years_range = (lower, upper)

    logging.info("Loading data from files...")
    data_manager = DataManager(emissions_path=emissions_path,
                               gdp_path=gdp_path,
                               population_path=population_path)
    full_df = data_manager.get_full_data()
    logging.info("Calculating summary statistics...")
    stats = Stats(full_df)
    try:
        emission_stats = stats.emission_stats_per_year(years_range)
        print(tabulate.tabulate(emission_stats, headers="keys", tablefmt="pqsl"))
    except EmptyIntervalException:
        logging.error("The specified time interval is too restritive: no data left. "
                      "Emission statistics are not available.")

    try:
        gdp_stats = stats.gdp_stats_per_year(years_range)
        print(tabulate.tabulate(gdp_stats, headers="keys", tablefmt="pqsl"))
    except EmptyIntervalException:
        logging.error("The specified time interval is too restrictive: no data left. "
                      "GDP statistics are not available.")
    emission_increase_stats, emission_decrease_stats = stats.emission_change_stats()
    if all(result.is_empty() for result in (emission_increase_stats, emission_decrease_stats)):
        logging.error("Cannot compute across-decade emission changes. "
                      "Most likely, there is no data available for the relevant years.")
    else:
        print(tabulate.tabulate(emission_increase_stats, headers="keys", tablefmt="pqsl", showindex="False"))
        print(tabulate.tabulate(emission_decrease_stats, headers="keys", tablefmt="pqsl", showindex="False"))


