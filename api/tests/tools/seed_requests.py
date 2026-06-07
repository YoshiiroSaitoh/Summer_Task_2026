from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable

from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class TemperatureRequest:
    probe_id: str
    recorded_at: str
    temperature: float


DEFAULT_BASE_URL = "http://localhost:8080"
REQUESTS: tuple[TemperatureRequest, ...] = (
    TemperatureRequest("probeA", "2026-06-07T09:00:00+09:00", 35.0),
    TemperatureRequest("probeA", "2026-06-07T09:00:10+09:00", 35.0),
    TemperatureRequest("probeB", "2026-06-07T09:00:00+09:00", 35.0),
    TemperatureRequest("probeB", "2026-06-07T09:00:10+09:00", 35.0),
)


def request_json(method: str, url: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: {error.code} {error.reason}: {error_body}") from error


def post_temperature(base_url: str, temperature_request: TemperatureRequest) -> dict[str, object]:
    return request_json(
        "POST",
        f"{base_url}/temperatures",
        {
            "probe_id": temperature_request.probe_id,
            "recorded_at": temperature_request.recorded_at,
            "temperature": temperature_request.temperature,
        },
    )


def get_latest_temperature(base_url: str, probe_id: str) -> dict[str, object]:
    return request_json("GET", f"{base_url}/temperatures/latest/{probe_id}")


def seed_requests(base_url: str) -> None:
    for temperature_request in REQUESTS:
        post_temperature(base_url, temperature_request)


def verify_latest_readings(base_url: str, probe_ids: Iterable[str]) -> None:
    for probe_id in probe_ids:
        response = get_latest_temperature(base_url, probe_id)
        print(f"{probe_id}: {response}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed demo temperature requests.")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Fetch the latest readings after seeding.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_requests(args.base_url)
    if args.verify:
        verify_latest_readings(args.base_url, ("probeA", "probeB"))


if __name__ == "__main__":
    main()
