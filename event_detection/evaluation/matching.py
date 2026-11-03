"""Ground-truth event matching with an explicit time tolerance."""

from collections.abc import Sequence
from datetime import timedelta

from event_detection.schemas import Event


def match_events(
    detected: Sequence[Event],
    ground_truth: Sequence[Event],
    tolerance_minutes: int = 15,
) -> dict[str, int]:
    """Match same-type events that start within the allowed time window."""

    tolerance = timedelta(minutes=tolerance_minutes)
    remaining = list(ground_truth)
    matched = 0
    for candidate in detected:
        match_index = next(
            (
                index for index, truth in enumerate(remaining)
                if truth.type == candidate.type
                and abs(truth.start - candidate.start) <= tolerance
            ),
            None,
        )
        if match_index is not None:
            remaining.pop(match_index)
            matched += 1
    return {
        "matched": matched,
        "detected": len(detected),
        "ground_truth": len(ground_truth),
    }
