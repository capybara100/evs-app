"""Dataset loaders that normalize source files into API-facing daily points."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from csv import DictReader
from datetime import datetime
from pathlib import Path

from event_detection.config import settings
from event_detection.schemas import SeriesPoint


class DatasetLoader(ABC):
    dataset_id: str

    @abstractmethod
    def load(self, household: str) -> Sequence[SeriesPoint]:
        """Load and normalize one household."""


class GridFlexLoader(DatasetLoader):
    dataset_id = "gridflex_heeten"

    def load(self, household: str) -> Sequence[SeriesPoint]:
        del household
        raise NotImplementedError("GridFlex source adapter is pending")


class ZonnedaelLoader(DatasetLoader):
    dataset_id = "zonnedael"

    _required_columns = {
        "household_id",
        "date",
        "electricity_kwh",
        "gas_m3",
        "n_elec_intervals",
        "n_gas_hours",
        "quality_flag",
        "woning_type",
        "bouwjaar_band",
        "gezinssituatie",
        "temp_mean_c",
        "temp_min_c",
        "temp_max_c",
        "hdd18",
    }

    def __init__(self, data_root: str | Path | None = None) -> None:
        root = Path(data_root or settings.data_root)
        if not root.is_absolute():
            root = Path(__file__).resolve().parents[2] / root
        self.data_root = root
        self._included_households = self._read_included_households()

    @property
    def included_households(self) -> set[str]:
        return self._included_households.copy()

    def _read_included_households(self) -> set[str]:
        """Read the homes that passed the data team's quality checks."""
        summary_path = self.data_root / "household_summary.csv"
        try:
            with summary_path.open(newline="", encoding="utf-8") as file:
                rows = DictReader(file)
                if not rows.fieldnames or not {"household_id", "included"} <= set(rows.fieldnames):
                    raise ValueError("household_summary.csv is missing household_id or included")
                return {
                    row["household_id"]
                    for row in rows
                    if row["included"].strip().lower() == "true"
                }
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Zonnedael summary file not found: {summary_path}") from error

    @staticmethod
    def _optional_float(value: str) -> float | None:
        return float(value) if value.strip() else None

    @staticmethod
    def _optional_int(value: str) -> int | None:
        return int(value) if value.strip() else None

    def load(self, household: str) -> Sequence[SeriesPoint]:
        """Read one household and keep the source's daily resolution."""
        if household not in self._included_households:
            raise ValueError(f"Household is not included in Zonnedael data: {household}")

        data_path = self.data_root / "zonnedael_daily_weather.csv"
        try:
            with data_path.open(newline="", encoding="utf-8") as file:
                rows = DictReader(file)
                columns = set(rows.fieldnames or ())
                missing = self._required_columns - columns
                if missing:
                    raise ValueError(f"Zonnedael data is missing columns: {sorted(missing)}")
                # Keep empty values empty; they are not zero consumption.
                points = [
                    self._row_to_point(row)
                    for row in rows
                    if row["household_id"] == household
                ]
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Zonnedael daily file not found: {data_path}") from error
        return sorted(points, key=lambda point: point.timestamp)

    def _row_to_point(self, row: dict[str, str]) -> SeriesPoint:
        """Convert one CSV row into the API's daily point format."""
        quality = row["quality_flag"].strip()
        if quality not in {"ok", "partial", "missing"}:
            raise ValueError(f"Unknown Zonnedael quality flag: {quality!r}")
        return SeriesPoint(
            timestamp=datetime.strptime(row["date"], "%Y-%m-%d"),
            electricity_kwh=self._optional_float(row["electricity_kwh"]),
            gas_m3=self._optional_float(row["gas_m3"]),
            quality_flag=quality,
            n_elec_intervals=self._optional_int(row["n_elec_intervals"]),
            n_gas_hours=self._optional_int(row["n_gas_hours"]),
            temp_mean_c=self._optional_float(row["temp_mean_c"]),
            temp_min_c=self._optional_float(row["temp_min_c"]),
            temp_max_c=self._optional_float(row["temp_max_c"]),
            hdd18=self._optional_float(row["hdd18"]),
            woning_type=row["woning_type"] or None,
            bouwjaar_band=row["bouwjaar_band"] or None,
            gezinssituatie=row["gezinssituatie"] or None,
        )
