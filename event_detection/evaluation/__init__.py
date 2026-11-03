"""Evaluation utilities kept separate from detector implementations."""

from .matching import match_events
from .scenarios import load_scenario

__all__ = ["load_scenario", "match_events"]
