\connect summer

CREATE TABLE IF NOT EXISTS temperature_logs (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NULL,
    experiment_run_id BIGINT NULL,
    probe_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    elapsed_seconds NUMERIC(12, 3) NULL,
    temperature NUMERIC(5, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    started_at TIMESTAMPTZ NULL,
    ended_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS probes (
    id BIGSERIAL PRIMARY KEY,
    probe_id VARCHAR(64) NOT NULL UNIQUE,
    deleted_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_probes (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NOT NULL,
    probe_id VARCHAR(64) NOT NULL,
    role VARCHAR(64) NOT NULL,
    valid_from TIMESTAMPTZ NULL,
    valid_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NOT NULL,
    label VARCHAR(128) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_experiments_status_started_at
    ON experiments (status, started_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_probes_probe_id_deleted_at
    ON probes (probe_id, deleted_at, updated_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_experiment_probes_probe_id_valid_from_valid_to
    ON experiment_probes (probe_id, valid_from DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_experiment_runs_experiment_id_started_at
    ON experiment_runs (experiment_id, started_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_temperature_logs_experiment_run_id_elapsed_seconds
    ON temperature_logs (experiment_run_id, elapsed_seconds);

CREATE OR REPLACE VIEW v_temperature_logs_grafana AS
SELECT
    tl.id AS temperature_log_id,
    tl.experiment_id,
    e.name AS experiment_name,
    tl.experiment_run_id,
    r.label AS run_label,
    tl.probe_id,
    p.role AS probe_role,
    tl.recorded_at,
    COALESCE(
        tl.elapsed_seconds,
        EXTRACT(EPOCH FROM (tl.recorded_at - r.started_at))
    ) AS elapsed_seconds,
    tl.temperature
FROM temperature_logs tl
LEFT JOIN experiments e
    ON e.id = tl.experiment_id
LEFT JOIN experiment_runs r
    ON r.id = tl.experiment_run_id
LEFT JOIN experiment_probes p
    ON p.experiment_id = tl.experiment_id
   AND p.probe_id = tl.probe_id
   AND (p.valid_from IS NULL OR p.valid_from <= tl.recorded_at)
   AND (p.valid_to IS NULL OR p.valid_to > tl.recorded_at);

ALTER TABLE temperature_logs OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE temperature_logs TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE temperature_logs_id_seq TO apluser;

ALTER TABLE experiments OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiments TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiments_id_seq TO apluser;

ALTER TABLE probes OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE probes TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE probes_id_seq TO apluser;

ALTER TABLE experiment_probes OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiment_probes TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiment_probes_id_seq TO apluser;

ALTER TABLE experiment_runs OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiment_runs TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiment_runs_id_seq TO apluser;
