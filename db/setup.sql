DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'apluser'
    ) THEN
        CREATE ROLE apluser LOGIN PASSWORD 'password';
    END IF;
END
$$;

DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_database
        WHERE datname = 'summer'
    ) THEN
        CREATE DATABASE summer OWNER apluser;
    END IF;
END
$$;

\connect summer

CREATE SCHEMA IF NOT EXISTS apluser AUTHORIZATION apluser;
ALTER ROLE apluser SET search_path = apluser, public;
ALTER DATABASE summer SET search_path = apluser, public;

GRANT ALL PRIVILEGES ON DATABASE summer TO apluser;
GRANT USAGE, CREATE ON SCHEMA apluser TO apluser;
