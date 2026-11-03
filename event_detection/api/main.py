"""Uvicorn entry point: python -m event_detection.api.main"""

import uvicorn

from .app import app


if __name__ == "__main__":
    # Keep this entry point useful when running the module directly.
    uvicorn.run(app, host="127.0.0.1", port=8000)
