"""Seed temperature data through the API."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from urllib import request

DEFAULT_BASE_URL = "http://localhost:8080"
DEFAULT_START_AT = "2026-06-07T09:00:00+09:00"
DEFAULT_INTERVAL_SECONDS = 10
DEFAULT_SAMPLE_COUNT = 360
DEFAULT_TEMPERATURE = 35.0
DEFAULT_PROBES = ("probeA", "probeB")


@dataclass(frozen=True)
class SeedItem:
    """Represents one API payload."""

    probe_id: str
    recorded_at: datetime
    temperature: float

    def to_json(self) -> bytes:
        """Serializes the payload for the API request."""
        return json.dumps(
            {
                "probe_id": self.probe_id,
                "recorded_at": self.recorded_at.isoformat(),
                "temperature": self.temperature,
            },
            ensure_ascii=False,
        ).encode("utf-8")


def build_items(
    probes: Iterable[str],
    start_at: datetime,
    interval_seconds: int,
    sample_count: int,
    temperature: float,
) -> list[SeedItem]:
    """Builds time-series seed items for each probe.

    Args:
        probes:
            Probe identifiers to seed.
        start_at:
            First timestamp.
        interval_seconds:
            Interval between samples.
        sample_count:
            Number of samples per probe.
        temperature:
            Temperature to send.

    Returns:
        Seed payloads ordered by probe and timestamp.
    """
    items: list[SeedItem] = []
    for probe_id in probes:
        for index in range(sample_count):
            items.append(
                SeedItem(
                    probe_id=probe_id,
                    recorded_at=start_at + timedelta(seconds=index * interval_seconds),
                    temperature=temperature,
                )
            )
    return items


def post_item(base_url: str, item: SeedItem) -> None:
    """Posts one seed item to the API.

    Args:
        base_url:
            API base URL.
        item:
            Payload to send.
    """
    api_url = f"{base_url.rstrip('/')}/temperatures"
    request_object = request.Request(
        api_url,
        data=item.to_json(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(request_object) as response:
        if response.status not in {200, 201}:
            raise RuntimeError(f"unexpected status: {response.status}")


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--start-at", default=DEFAULT_START_AT)
    parser.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument("--sample-count", type=int, default=DEFAULT_SAMPLE_COUNT)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--probe", action="append", dest="probes")
    return parser.parse_args()


def main() -> int:
    """Seeds the API with demo temperature readings.

    Returns:
        Process exit status.
    """
    args = parse_args()
    probes = tuple(args.probes) if args.probes else DEFAULT_PROBES
    start_at = datetime.fromisoformat(args.start_at)
    items = build_items(
        probes=probes,
        start_at=start_at,
        interval_seconds=args.interval_seconds,
        sample_count=args.sample_count,
        temperature=args.temperature,
    )

    for item in items:
        post_item(args.base_url, item)
        print(f"posted {item.probe_id} {item.recorded_at.isoformat()}")

    print(f"seeded {len(items)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
