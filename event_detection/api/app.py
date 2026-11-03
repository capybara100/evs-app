"""Standalone HTTP API for event detection."""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from event_detection.config import settings
from event_detection.data import available_datasets, get_series
from event_detection.anomaly.placeholder import PlaceholderAnomalyDetector
from event_detection.evaluation.matching import match_events
from event_detection.evaluation.scenarios import load_scenario
from event_detection.nilm import detector_registry
from event_detection.schemas import (
    DetectRequest,
    EvaluationMetric,
    EvaluationRequest,
    EvaluationResponse,
)

app = FastAPI(title=settings.api_title)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Small landing response for a browser or service health check."""

    return {
        "service": settings.api_title,
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/datasets", "/series", "/detect", "/evaluate"],
    }


@app.get("/datasets")
def datasets():
    """List the datasets known by the service."""
    return available_datasets()


@app.get("/series")
def series(
    dataset: str,
    household: str,
    range_start: datetime | None = None,
    range_end: datetime | None = None,
):
    """Return one household's daily readings."""
    try:
        return get_series(dataset, household, range_start, range_end)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/detect")
def detect(request: DetectRequest):
    """Run the selected detector for one household and date range."""
    try:
        points = get_series(request.dataset, request.household, request.range_start, request.range_end)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if request.module == "nilm":
        try:
            detector = detector_registry.get(request.method)
        except KeyError as error:
            raise HTTPException(status_code=400, detail="Unknown NILM method") from error
    else:
        detector = PlaceholderAnomalyDetector()
    return detector.detect(points)


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest):
    """Compare the rules with one prepared synthetic scenario."""
    if request.dataset != "zonnedael":
        raise HTTPException(status_code=400, detail="Scenario evaluation is only available for Zonnedael")
    if request.module != "nilm":
        raise HTTPException(status_code=400, detail="Scenario evaluation requires the NILM rules module")
    # Scenarios currently contain prepared data for this home only.
    fixture_household = "Klant 34"
    try:
        points, ground_truth, quality = load_scenario(request.scenario, fixture_household)
        detector = detector_registry.get(request.method)
    except (FileNotFoundError, KeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    # Apply the requested date range to both detections and truth.
    points = [
        point for point in points
        if (request.range_start is None or point.timestamp >= request.range_start)
        and (request.range_end is None or point.timestamp <= request.range_end)
    ]
    ground_truth = [
        event for event in ground_truth
        if (request.range_start is None or event.start >= request.range_start)
        and (request.range_end is None or event.start <= request.range_end)
    ]
    detected = detector.detect(points)
    event_types = sorted({event.type for event in detected} | {event.type for event in ground_truth})
    metrics = []
    for event_type in event_types:
        # Calculate each event type separately so unrelated patterns do not mix.
        result = match_events(
            [event for event in detected if event.type == event_type],
            [event for event in ground_truth if event.type == event_type],
            request.tolerance_minutes,
        )
        precision = result["matched"] / result["detected"] if result["detected"] else 0
        recall = result["matched"] / result["ground_truth"] if result["ground_truth"] else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        metrics.append(EvaluationMetric(
            event_type=event_type,
            precision=round(precision, 3),
            recall=round(recall, 3),
            f1=round(f1, 3),
            **result,
        ))
    return EvaluationResponse(
        metrics=metrics,
        tolerance_minutes=request.tolerance_minutes,
        source=f"synthetic ground truth from Zonnedael scenario '{request.scenario}' for {fixture_household}",
        notes=[
            "Synthetic events are evaluation fixtures, not appliance labels.",
            "Partial, missing, and absent dates are reported as data quality and excluded from detection.",
        ],
        data_quality=quality,
    )
