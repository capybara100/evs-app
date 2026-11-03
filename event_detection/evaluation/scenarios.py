"""Scenario fixtures and synthetic ground truth for detector evaluation."""

import csv
from datetime import datetime, timedelta
from pathlib import Path

from event_detection.config import settings
from event_detection.schemas import DataQualityIssue, Event, SeriesPoint

SCENARIO_NAMES = ("normal", "high_use", "missing", "incomplete")


def load_scenario(name: str, household: str) -> tuple[list[SeriesPoint], list[Event], list[DataQualityIssue]]:
    """Load fixture data, synthetic events, and data-quality findings."""
    if name not in SCENARIO_NAMES:
        raise ValueError(f"Unknown evaluation scenario: {name}")
    if household != "Klant 34":
        raise ValueError("Evaluation scenarios are only available for Klant 34")

    path = _scenario_path(name)
    points: list[SeriesPoint] = []
    truth: list[Event] = []
    quality: list[DataQualityIssue] = []
    with path.open(newline="", encoding="utf-8") as file:
        # The extra scenario columns are only used to build test expectations.
        for row in csv.DictReader(file):
            point = _point_from_row(row)
            points.append(point)
            if row.get("synthetic_event", "").lower() == "true":
                assert point.gas_m3 is not None
                truth.append(
                    Event(
                        id=f"synthetic:{point.timestamp.isoformat()}",
                        type="high_gas",
                        start=point.timestamp,
                        end=point.timestamp + timedelta(days=1),
                        magnitude=point.gas_m3,
                        confidence=1,
                        method="synthetic_ground_truth",
                    )
                )
            if point.quality_flag != "ok":
                quality.append(
                    DataQualityIssue(
                        date=point.timestamp,
                        status=point.quality_flag,
                        details="Meter reading is not complete and was excluded from detection.",
                    )
                )

    # A missing row is different from a row marked as missing.
    dates = {point.timestamp.date() for point in points}
    if points:
        current = min(dates)
        last = max(dates)
        while current <= last:
            if current not in dates:
                quality.append(
                    DataQualityIssue(
                        date=datetime.combine(current, datetime.min.time()),
                        status="gap",
                        details="No row was supplied for this date.",
                    )
                )
            current += timedelta(days=1)
    quality.sort(key=lambda issue: issue.date)
    return points, truth, quality


def _scenario_path(name: str) -> Path:
    root = Path(settings.data_root)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[2] / root
    return root / "scenarios" / f"{name}.csv"


def _optional_float(value: str) -> float | None:
    return float(value) if value else None


def _point_from_row(row: dict[str, str]) -> SeriesPoint:
    return SeriesPoint(
        timestamp=datetime.strptime(row["date"], "%Y-%m-%d"),
        electricity_kwh=_optional_float(row["electricity_kwh"]),
        gas_m3=_optional_float(row["gas_m3"]),
        quality_flag=row["quality_flag"],
        n_elec_intervals=int(row["n_elec_intervals"]) if row["n_elec_intervals"] else None,
        n_gas_hours=int(row["n_gas_hours"]) if row["n_gas_hours"] else None,
        temp_mean_c=_optional_float(row["temp_mean_c"]),
        temp_min_c=_optional_float(row["temp_min_c"]),
        temp_max_c=_optional_float(row["temp_max_c"]),
        hdd18=_optional_float(row["hdd18"]),
        woning_type=row["woning_type"] or None,
        bouwjaar_band=row["bouwjaar_band"] or None,
        gezinssituatie=row["gezinssituatie"] or None,
    )
