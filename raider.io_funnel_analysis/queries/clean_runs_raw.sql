/* Drop rows with anonymized characters or bad data */
DELETE FROM runs_raw
WHERE
    name ~ '^Anon[A-Z0-9]{7}$'
   OR realm = 'Anonymous'
   OR dungeon IS NULL
   OR dungeon_short IS NULL
   OR level IS NULL
   OR timestamp IS NULL
   OR timestamp::timestamptz IS NULL
   OR status IS NULL
   OR num_chests IS NULL
   OR score IS NULL
   OR name IS NULL
   OR realm IS NULL
   OR class IS NULL
   OR spec IS NULL
   OR role IS NULL;

ALTER TABLE runs_raw
    ALTER COLUMN timestamp
        TYPE timestamptz
        USING timestamp::timestamptz;

CREATE INDEX idx_raw
    ON runs_raw (name, realm, class, spec);