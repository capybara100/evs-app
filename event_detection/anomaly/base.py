"""Shared anomaly detector interface."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from event_detection.schemas import Event, SeriesPoint


class AnomalyDetector(ABC):
    name: str

    @abstractmethod
    def detect(self, series: Sequence[SeriesPoint]) -> list[Event]:
        """Detect anomalies without coupling callers to an algorithm."""
