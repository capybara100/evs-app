"""Detector interface and registry shared by future NILM methods."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from event_detection.schemas import Event, SeriesPoint


class Detector(ABC):
    """Stable detector contract; API code does not depend on an algorithm."""

    name: str

    @abstractmethod
    def detect(self, series: Sequence[SeriesPoint]) -> list[Event]:
        """Detect events from one normalized series."""


class DetectorRegistry:
    def __init__(self) -> None:
        self._detectors: dict[str, Detector] = {}

    def register(self, detector: Detector) -> None:
        self._detectors[detector.name] = detector

    def get(self, name: str) -> Detector:
        return self._detectors[name]

    def names(self) -> list[str]:
        return sorted(self._detectors)


detector_registry = DetectorRegistry()
