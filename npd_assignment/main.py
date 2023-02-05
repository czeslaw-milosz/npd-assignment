import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
        "-e",
        "--emissions_file",
        type=str,
        required=True,
        help="Path to .csv file containing the emissions data.",
    )
    parser.add_argument(
        "-start",
        type=int,
        required=False,
        help="Beginning of the required time interval [in years].",
    )
    parser.add_argument(
        "-koniec",
        type=int,
        required=False,
        help="Beginning of the required time interval [in years].",
    )

    args = parser.parse_args()
    if (args.start is None) ^ (args.koniec is None):
        parser.error("start i koniec muszą być podane łącznie!")
