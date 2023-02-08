import argparse
import logging

import tabulate

from npd_assignment import utils
from npd_assignment.analysis import Stats
from npd_assignment.data_management import DataManager
from npd_assignment.exceptions import EmptyIntervalException


logging.basicConfig(level=logging.INFO)

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
        "-d",
        "--display_mode",
        type=str,
        required=False,
        choices=["plain", "pretty"],
        default="plain",
        help="Display mode for results; 'plain' is less pretty "
        "but handles multi-indexing well; "
        "'pretty' has opposite properties to 'plain'. "
        "Single-indexed tables will always be displayed in pretty mode.",
    )
    parser.add_argument(
        "-start",
        type=int,
        required=False,
        help="Beginning of the requested time interval [in years]. "
        "Will be used to filter the data.",
    )
    parser.add_argument(
        "-koniec",
        type=int,
        required=False,
        help="Beginning of the requested time interval [in years]. "
        "Will be used to filter the data.",
    )

    args = parser.parse_args()

    logging.info("Loading data from files...\n")
    data_manager = DataManager(
        emissions_path=args.emissions_file,
        gdp_path=args.gdp_file,
        population_path=args.population_file,
    )
    data_manager.load_data()
    full_df = data_manager.get_full_data()
    logging.info("Calculating summary statistics...\n")
    stats = Stats(full_df)
    try:
        emission_stats = stats.emission_stats_per_year(
            year_range=(args.start, args.koniec)
        )
        emission_stats = utils.reindex_grouped_table(
            emission_stats, index_names=["Year", "ID"]
        )
        print("\n")
        if args.display_mode == "pretty":
            print(
                tabulate.tabulate(
                    emission_stats, headers="keys", tablefmt="pretty"
                )
            )
        else:
            print(emission_stats.to_string())
        print("\n")
    except EmptyIntervalException:
        logging.error(
            "The specified time interval is too restritive: no data left. "
            "Emission statistics are not available."
        )

    try:
        gdp_stats = stats.gdp_stats_per_year(
            year_range=(args.start, args.koniec)
        )
        gdp_stats = utils.reindex_grouped_table(
            gdp_stats, index_names=["Year", "ID"]
        )
        print("\n")
        if args.display_mode == "pretty":
            print(
                tabulate.tabulate(gdp_stats, headers="keys", tablefmt="pretty")
            )
        else:
            print(gdp_stats.to_string())
    except EmptyIntervalException:
        logging.error(
            "The specified time interval is too restrictive: no data left. "
            "GDP statistics are not available."
        )
    (
        emission_increase_stats,
        emission_decrease_stats,
    ) = stats.emission_change_stats()
    if all(
        result.empty
        for result in (emission_increase_stats, emission_decrease_stats)
    ):
        logging.error(
            "Cannot compute across-decade emission changes. "
            "Most likely, there is no data available for the relevant years."
        )
    else:
        print("\n")
        print(
            tabulate.tabulate(
                emission_increase_stats,
                headers="keys",
                tablefmt="pretty",
                showindex="False",
            )
        )
        print("\n")
        print(
            tabulate.tabulate(
                emission_decrease_stats,
                headers="keys",
                tablefmt="pretty",
                showindex="True",
            )
        )
