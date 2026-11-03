from datetime import datetime, timezone

from event_detection.evaluation.matching import match_events
from event_detection.evaluation.scenarios import load_scenario
from event_detection.schemas import Event


def test_matching_uses_a_configurable_time_tolerance():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    detected = [
        Event(
            id="d",
            type="step_change",
            start=start,
            end=start,
            magnitude=10,
            confidence=.5,
            method="rules",
        )
    ]
    truth = [
        Event(
            id="t",
            type="step_change",
            start=start.replace(minute=15),
            end=start,
            magnitude=10,
            confidence=1,
            method="ground_truth",
        )
    ]
    assert match_events(detected, truth)["matched"] == 1
    assert match_events(detected, truth, tolerance_minutes=0)["matched"] == 0


def test_high_use_scenario_exposes_synthetic_truth():
    # This fixture contains four known artificial gas increases.
    points, truth, quality = load_scenario("high_use", "Klant 34")
    assert len(points) == 90
    assert len(truth) == 4
    assert {event.type for event in truth} == {"high_gas"}
    assert quality == []


def test_missing_scenario_separates_quality_from_truth():
    # Gaps and incomplete rows are reported separately from events.
    points, truth, quality = load_scenario("missing", "Klant 34")
    assert len(points) == 88
    assert truth == []
    assert [issue.status for issue in quality].count("missing") == 3
    assert [issue.status for issue in quality].count("partial") == 3
    assert [issue.status for issue in quality].count("gap") == 2
