CREATE TABLE temperature_logs (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NULL,
    experiment_run_id BIGINT NULL,
    probe_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    elapsed_seconds NUMERIC(12, 3) NULL,
    temperature NUMERIC(5, 2) NOT NULL
);

CREATE TABLE experiments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description VARCHAR(512) NULL,
    status VARCHAR(32) NOT NULL,
    started_at TIMESTAMPTZ NULL,
    ended_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    archived_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE probes (
    id BIGSERIAL PRIMARY KEY,
    probe_id VARCHAR(64) NOT NULL UNIQUE,
    deleted_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE experiment_probes (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NOT NULL,
    probe_id VARCHAR(64) NOT NULL,
    role VARCHAR(64) NOT NULL,
    valid_from TIMESTAMPTZ NULL,
    valid_to TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE experiment_runs (
    id BIGSERIAL PRIMARY KEY,
    experiment_id BIGINT NOT NULL,
    label VARCHAR(128) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
