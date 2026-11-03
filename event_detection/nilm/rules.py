"""Documented baseline rules for unusual daily aggregate consumption."""

from collections.abc import Sequence
from datetime import timedelta
from statistics import median

from event_detection.schemas import Event, SeriesPoint
from .base import Detector, detector_registry


class RuleBasedDetector(Detector):
    """Flag valid daily readings that are substantially above a baseline.

    Electricity uses the household median. Gas uses a least-squares relationship
    with heating degree days so cold-weather heating is not treated as unusual.
    Partial and missing points never contribute to a baseline or event.
    """

    name = "rules"
    electricity_ratio = 1.75
    electricity_delta_kwh = 5.0
    gas_ratio = 1.4
    gas_delta_m3 = 4.0

    def detect(self, series: Sequence[SeriesPoint]) -> list[Event]:
        """Compare valid readings with electricity and gas baselines."""
        valid = [point for point in series if point.quality_flag == "ok"]
        events: list[Event] = []
        electricity = [
            point.electricity_kwh for point in valid if point.electricity_kwh is not None
        ]
        if electricity:
            baseline = median(electricity)
            for point in valid:
                value = point.electricity_kwh
                is_high = (
                    value is not None
                    and value >= baseline * self.electricity_ratio
                    and value - baseline >= self.electricity_delta_kwh
                )
                if is_high:
                    events.append(self._event(point, "high_electricity", value, baseline))

        gas_points = [
            point for point in valid
            if point.gas_m3 is not None and point.hdd18 is not None
        ]
        if len(gas_points) >= 3:
            # Heating degree days make cold-day gas use less surprising.
            intercept, slope = self._gas_baseline(gas_points)
            for point in gas_points:
                assert point.gas_m3 is not None and point.hdd18 is not None
                baseline = max(0.0, intercept + slope * point.hdd18)
                is_high = (
                    point.gas_m3 >= baseline * self.gas_ratio
                    and point.gas_m3 - baseline >= self.gas_delta_m3
                )
                if is_high:
                    events.append(self._event(point, "high_gas", point.gas_m3, baseline))
        return sorted(events, key=lambda event: event.start)

    @staticmethod
    def _gas_baseline(points: Sequence[SeriesPoint]) -> tuple[float, float]:
        """Fit a straight line between heating degree days and gas use."""
        x_values = [point.hdd18 for point in points if point.hdd18 is not None]
        y_values = [point.gas_m3 for point in points if point.gas_m3 is not None]
        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(y_values) / len(y_values)
        denominator = sum((value - x_mean) ** 2 for value in x_values)
        slope = (
            sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            / denominator
            if denominator
            else 0.0
        )
        return y_mean - slope * x_mean, slope

    def _event(self, point: SeriesPoint, event_type: str, value: float, baseline: float) -> Event:
        """Build a generic event without guessing an appliance."""
        return Event(
            id=f"{event_type}:{point.timestamp.isoformat()}",
            type=event_type,
            start=point.timestamp,
            end=point.timestamp + timedelta(days=1),
            magnitude=round(value - baseline, 3),
            confidence=min(1.0, round((value - baseline) / max(value, 1e-9), 3)),
            method=self.name,
            details={
                "observed": value,
                "baseline": round(baseline, 3),
                "quality_flag": point.quality_flag,
            },
        )


detector_registry.register(RuleBasedDetector())
