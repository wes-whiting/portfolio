/* Drop rows with anonymized characters or bad data */
DELETE FROM runs_raw
WHERE
    name ~ '^Anon[A-Z0-9]{7}$'
    OR realm = 'Anonymous'
    OR dungeon IS NULL
    OR dungeon_short IS NULL
    OR completed_at IS NULL
    OR completed_at::timestamptz IS NULL
    OR score IS NULL
    OR name IS NULL
    OR realm IS NULL
    OR class IS NULL
    OR spec IS NULL
    OR role IS NULL
    OR race IS NULL
    OR faction IS NULL;

ALTER TABLE runs_raw
    ALTER COLUMN completed_at
        TYPE timestamptz
        USING completed_at::timestamptz;

CREATE INDEX idx_raw
    ON runs_raw (name, realm, class, spec);