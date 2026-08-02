\set ON_ERROR_STOP on
\connect summer

BEGIN;

CREATE TABLE IF NOT EXISTS experiment_run_probes (
    id BIGSERIAL PRIMARY KEY,
    experiment_run_id BIGINT NOT NULL REFERENCES experiment_runs(id),
    probe_id VARCHAR(64) NOT NULL REFERENCES probes(probe_id),
    role VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_experiment_run_probes_run_probe UNIQUE (experiment_run_id, probe_id)
);

CREATE INDEX IF NOT EXISTS idx_experiment_run_probes_probe_id_run_id
    ON experiment_run_probes (probe_id, experiment_run_id);

INSERT INTO experiment_run_probes (
    experiment_run_id,
    probe_id,
    role,
    created_at,
    updated_at
)
SELECT DISTINCT ON (r.id, p.probe_id)
    r.id,
    p.probe_id,
    p.role,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM experiment_probes p
JOIN experiment_runs r
    ON r.experiment_id = p.experiment_id
   AND COALESCE(p.valid_to, 'infinity'::timestamptz) > r.started_at
   AND COALESCE(r.ended_at, 'infinity'::timestamptz)
       > COALESCE(p.valid_from, '-infinity'::timestamptz)
ORDER BY r.id, p.probe_id, p.valid_from DESC NULLS LAST, p.id DESC
ON CONFLICT (experiment_run_id, probe_id) DO NOTHING;

CREATE OR REPLACE VIEW v_temperature_logs_grafana AS
SELECT
    tl.id AS temperature_log_id,
    tl.experiment_id,
    e.name AS experiment_name,
    tl.experiment_run_id,
    r.label AS run_label,
    tl.probe_id,
    rp.role AS probe_role,
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
LEFT JOIN experiment_run_probes rp
    ON rp.experiment_run_id = tl.experiment_run_id
   AND rp.probe_id = tl.probe_id;

ALTER TABLE experiment_run_probes OWNER TO apluser;
ALTER VIEW v_temperature_logs_grafana OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE experiment_run_probes TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE experiment_run_probes_id_seq TO apluser;
GRANT SELECT ON v_temperature_logs_grafana TO apluser;

COMMIT;
