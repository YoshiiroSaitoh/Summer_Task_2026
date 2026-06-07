\connect summer

CREATE TABLE IF NOT EXISTS temperature_logs (
    id BIGSERIAL PRIMARY KEY,
    probe_id VARCHAR(64) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL
);

ALTER TABLE temperature_logs OWNER TO apluser;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE temperature_logs TO apluser;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE temperature_logs_id_seq TO apluser;
