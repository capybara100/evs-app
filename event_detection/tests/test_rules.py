from datetime import datetime

from event_detection.anomaly.placeholder import PlaceholderAnomalyDetector
from event_detection.nilm.rules import RuleBasedDetector
from event_detection.schemas import SeriesPoint


def test_rule_detector_ignores_invalid_points():
    # A bad reading must not become a false consumption event.
    series = [
        SeriesPoint(timestamp=datetime(2026, 1, 1), electricity_kwh=10, gas_m3=5, hdd18=10, quality_flag="ok"),
        SeriesPoint(timestamp=datetime(2026, 1, 2), electricity_kwh=10, gas_m3=5, hdd18=10, quality_flag="ok"),
        SeriesPoint(timestamp=datetime(2026, 1, 3), electricity_kwh=None, gas_m3=None, hdd18=10, quality_flag="missing"),
    ]
    assert RuleBasedDetector().detect(series) == []
    assert PlaceholderAnomalyDetector().detect(series) == []


def test_rule_detector_reports_generic_elevated_consumption():
    # Rules describe the pattern, not the appliance behind it.
    series = [
        SeriesPoint(timestamp=datetime(2026, 1, 1), electricity_kwh=10, gas_m3=5, hdd18=10, quality_flag="ok"),
        SeriesPoint(timestamp=datetime(2026, 1, 2), electricity_kwh=11, gas_m3=5.5, hdd18=10, quality_flag="ok"),
        SeriesPoint(timestamp=datetime(2026, 1, 3), electricity_kwh=20, gas_m3=12, hdd18=10, quality_flag="ok"),
    ]
    events = RuleBasedDetector().detect(series)
    assert {event.type for event in events} == {"high_electricity", "high_gas"}
    assert all("baseline" in event.details for event in events)
