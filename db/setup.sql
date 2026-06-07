\set ON_ERROR_STOP on

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

SELECT format('CREATE DATABASE %I OWNER %I', 'summer', 'apluser')
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = 'summer'
)
\gexec

\connect summer

CREATE SCHEMA IF NOT EXISTS apluser AUTHORIZATION apluser;
ALTER ROLE apluser SET search_path = apluser, public;
ALTER DATABASE summer SET search_path = apluser, public;

GRANT ALL PRIVILEGES ON DATABASE summer TO apluser;
GRANT USAGE, CREATE ON SCHEMA apluser TO apluser;
