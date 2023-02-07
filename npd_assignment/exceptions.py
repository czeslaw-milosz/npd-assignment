from typing import Tuple


class EmptyIntervalException(Exception):
    def __init__(self, interval: Tuple[int, int], *args) -> None:
        super().__init__(f"No data available for the requested year interval {interval}", *args)
