from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Temperature Log API", version="0.1.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Returns a simple health response."""

    return {"status": "ok"}
