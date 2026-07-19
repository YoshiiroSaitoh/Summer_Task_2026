\connect summer

CREATE TABLE IF NOT EXISTS temperature_logs (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NULL,
    probe_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_experiments_status_started_at
    ON experiments (status, started_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_experiment_probes_probe_id_valid_from_valid_to
    ON experiment_probes (probe_id, valid_from DESC, id DESC);

ALTER TABLE temperature_logs OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE temperature_logs TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE temperature_logs_id_seq TO apluser;

ALTER TABLE experiments OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiments TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiments_id_seq TO apluser;

ALTER TABLE experiment_probes OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiment_probes TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiment_probes_id_seq TO apluser;
