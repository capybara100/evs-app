"""Placeholder anomaly implementation."""

from collections.abc import Sequence

from event_detection.schemas import Event, SeriesPoint
from .base import AnomalyDetector


class PlaceholderAnomalyDetector(AnomalyDetector):
    """Keep the anomaly module available until a real method is chosen."""

    name = "placeholder"

    def detect(self, series: Sequence[SeriesPoint]) -> list[Event]:
        """Return no events until an anomaly method is implemented."""
        del series
        return []
