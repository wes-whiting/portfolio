/* Drop rows with anonymized characters or bad data */
-- DELETE FROM runs_raw
--     WHERE
--         name ~ '^Anon[A-Z0-9]{7}$'
--         OR realm = 'Anonymous'
--         OR name IS NULL
--         OR realm IS NULL
--         OR class IS NULL
--         OR dungeon IS NULL
--         OR dungeon_short IS NULL
--         OR score IS NULL
--         OR timestamp IS NULL;

-- ALTER TABLE runs_raw
--     RENAME COLUMN "time" to "timestamp";

-- ALTER TABLE runs_raw
--     ALTER COLUMN timestamp
--         TYPE timestamptz
--         USING timestamp::timestamptz;

-- CREATE INDEX idx_raw
--     ON runs_raw (name, realm, class)

-- CREATE INDEX idx_raw_persona
--     ON runs_raw (persona_id);

-- DROP TABLE IF EXISTS characters;
-- CREATE TABLE characters AS
-- SELECT DISTINCT name, realm, class, id, persona_id
-- FROM runs_raw;

DROP TABLE IF EXISTS characters;
CREATE TABLE characters AS
SELECT DISTINCT class, persona_id
FROM runs_raw;

DROP TABLE IF EXISTS dungeons;
CREATE TABLE dungeons AS
SELECT DISTINCT dungeon, dungeon_short
FROM runs_raw;

DO $$
DECLARE
    make_score_columns text;
    sum_score_columns text;
    maketable text;
BEGIN
    /* Build the running max commands for each dungeon dynamically */
    SELECT string_agg(
        DISTINCT format(
            'max (CASE WHEN dungeon = %L THEN score ELSE 0 END)
            OVER (
                PARTITION BY persona_id
                ORDER BY timestamp
                ROWS BETWEEN unbounded preceding AND current row
            ) AS %I',
            dungeon,
            dungeon_short
        ),
        E',\n'
    )
    INTO make_score_columns
    FROM dungeons;

    /* Build the sum expression over dungeons */
    SELECT string_agg(
           format('%I', dungeon_short),
           ' + '
    )
    INTO sum_score_columns
    FROM dungeons;

    /* Build the entire CREATE TABLE statement with above commands */
    maketable := format(
        'CREATE TABLE runs_enriched AS
        SELECT persona_id, class, (%s) AS total_score, timestamp, dungeon, score
        FROM (
            SELECT persona_id, class, dungeon, timestamp, score, %s
            FROM runs_raw
        ) t',
        sum_score_columns,
        make_score_columns
    );

    EXECUTE 'DROP TABLE IF EXISTS runs_enriched';
    EXECUTE maketable;
END $$;

-- CREATE INDEX idx_enriched
--     ON runs_enriched (name, realm, class);

CREATE INDEX idx_enriched_persona
    ON runs_enriched (persona_id);

-- Make timestamp columns for rating thresholds
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS ksc timestamptz,
    ADD COLUMN IF NOT EXISTS ksm timestamptz,
    ADD COLUMN IF NOT EXISTS ksh timestamptz,
    ADD COLUMN IF NOT EXISTS ksl timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_two_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_four_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_six_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS title timestamptz;

-- UPDATE characters
--     SET
--         ksc = subquery.ksc,
--         ksm = subquery.ksm,
--         ksh = subquery.ksh,
--         ksl = subquery.ksl,
--         thirty_two_hundred = subquery.thirty_two_hundred,
--         thirty_four_hundred = subquery.thirty_four_hundred,
--         thirty_six_hundred = subquery.thirty_six_hundred,
--         title = subquery.title
--     FROM (
--         SELECT
--             name,
--             realm,
--             class,
--             min(timestamp) FILTER (WHERE total_score >= 1500) AS ksc,
--             min(timestamp) FILTER (WHERE total_score >= 2000) AS ksm,
--             min(timestamp) FILTER (WHERE total_score >= 2500) AS ksh,
--             min(timestamp) FILTER (WHERE total_score >= 3000) AS ksl,
--             min(timestamp) FILTER (WHERE total_score >= 3200) AS thirty_two_hundred,
--             min(timestamp) FILTER (WHERE total_score >= 3400) AS thirty_four_hundred,
--             min(timestamp) FILTER (WHERE total_score >= 3600) AS thirty_six_hundred,
--             min(timestamp) FILTER (WHERE total_score >= 3804.8) AS title
--         FROM runs_enriched
--         GROUP BY name, realm, class
--         ) as subquery
--     WHERE
--         characters.name = subquery.name
--         AND characters.realm = subquery.realm
--         AND characters.class = subquery.class;

UPDATE characters
SET
    ksc = subquery.ksc,
    ksm = subquery.ksm,
    ksh = subquery.ksh,
    ksl = subquery.ksl,
    thirty_two_hundred = subquery.thirty_two_hundred,
    thirty_four_hundred = subquery.thirty_four_hundred,
    thirty_six_hundred = subquery.thirty_six_hundred,
    title = subquery.title
FROM (
         SELECT
             persona_id,
             class,
             min(timestamp) FILTER (WHERE total_score >= 1500) AS ksc,
             min(timestamp) FILTER (WHERE total_score >= 2000) AS ksm,
             min(timestamp) FILTER (WHERE total_score >= 2500) AS ksh,
             min(timestamp) FILTER (WHERE total_score >= 3000) AS ksl,
             min(timestamp) FILTER (WHERE total_score >= 3200) AS thirty_two_hundred,
             min(timestamp) FILTER (WHERE total_score >= 3400) AS thirty_four_hundred,
             min(timestamp) FILTER (WHERE total_score >= 3600) AS thirty_six_hundred,
             min(timestamp) FILTER (WHERE total_score >= 3804.8) AS title
         FROM runs_enriched
         GROUP BY persona_id, class
     ) as subquery
WHERE
    characters.persona_id = subquery.persona_id
    AND characters.class = subquery.class;