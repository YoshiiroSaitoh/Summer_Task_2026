\set ON_ERROR_STOP on

INSERT INTO temperature_logs (probe_id, recorded_at, temperature)
SELECT
    'probeA',
    timestamp '2026-06-07 09:00:00+09' + make_interval(secs => series_value * 10),
    35.00
FROM generate_series(0, 359) AS series_value;

INSERT INTO temperature_logs (probe_id, recorded_at, temperature)
SELECT
    'probeB',
    timestamp '2026-06-07 09:00:00+09' + make_interval(secs => series_value * 10),
    35.00
FROM generate_series(0, 359) AS series_value;
