"""Dataset catalog and access to normalized daily observations."""

from datetime import datetime

from event_detection.schemas import DatasetInfo, SeriesPoint
from .loaders import ZonnedaelLoader

_ZONNEDAEL_LOADER = ZonnedaelLoader()

_DATASETS = [
    DatasetInfo(
        id="gridflex_heeten",
        name="GridFlex Heeten",
        households=[],
        resolution_minutes=15,
        available=False,
        notes="Loader pending; source data is 1-minute and must be resampled to 15 minutes.",
    ),
    DatasetInfo(
        id="zonnedael",
        name="Zonnedael",
        households=sorted(_ZONNEDAEL_LOADER.included_households),
        resolution_minutes=1440,
        available=True,
        notes="Daily T+1 aggregate data for included households. Missing and partial days are preserved.",
    ),
]


def available_datasets() -> list[DatasetInfo]:
    """Return the datasets that can currently be selected."""

    return _DATASETS.copy()


_LOADERS = {"zonnedael": _ZONNEDAEL_LOADER}


def get_series(
    dataset: str,
    household: str,
    range_start: datetime | None = None,
    range_end: datetime | None = None,
) -> list[SeriesPoint]:
    """Return one household's daily points, optionally restricted by date."""

    try:
        loader = _LOADERS[dataset]
    except KeyError as error:
        raise ValueError(f"Unknown dataset: {dataset}") from error
    points = loader.load(household)
    return [
        point
        for point in points
        if (range_start is None or point.timestamp >= range_start)
        and (range_end is None or point.timestamp <= range_end)
    ]
