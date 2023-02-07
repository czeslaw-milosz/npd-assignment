from typing import Tuple

from .config import CONFIG


class EmptyIntervalException(Exception):
    def __init__(self, interval: Tuple[int, int], *args) -> None:
        super().__init__(f"No data available for the requested year interval {interval}", *args)


class MissingColumnsException(Exception):
    def __init__(self, *args) -> None:
        super().__init__(f"The dataframe you provided is missing some columns. Columns required by Stats object are: "
                         f"{CONFIG['stats_required_columns']}", *args)
