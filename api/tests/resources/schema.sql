CREATE TABLE temperature_logs (
    id BIGSERIAL PRIMARY KEY,
    probe_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL
);
