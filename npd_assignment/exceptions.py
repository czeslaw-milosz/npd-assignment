"""Custom exceptions used within the package."""

from typing import Tuple, Optional

from npd_assignment.config import CONFIG


class EmptyIntervalException(Exception):
    """Indicates that no data was left in df after narrowing years range."""
    def __init__(
        self, interval: Tuple[Optional[int], Optional[int]], *args
    ) -> None:
        super().__init__(
            f"No data available for the requested year interval {interval}",
            *args,
        )


class MissingColumnsException(Exception):
    """Indicates missing columns in df passed to analysis.Stats.__init__()"""
    def __init__(self, *args) -> None:
        super().__init__(
            f"The dataframe you provided is missing some columns. "
            f"Columns required by Stats object are: "
            f"{CONFIG['stats_required_columns']}",
            *args,
        )
