/* Make dungeon table */
DROP TABLE IF EXISTS dungeons;
CREATE TABLE dungeons AS
SELECT DISTINCT dungeon, dungeon_short
FROM runs_raw;

/* Make run table with score running maxes */
DO $$
DECLARE
    make_score_columns text;
    sum_score_columns text;
    maketable text;
BEGIN
    /* Dynamically build the running max commands for each dungeon */
    SELECT string_agg(
        DISTINCT format(
        'max (CASE WHEN dungeon = %L THEN score ELSE 0 END)
        OVER (
            PARTITION BY name, realm, class, spec
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
        SELECT *, (%s) AS total_score
        FROM (
            SELECT name, realm, class, spec, dungeon, timestamp, score, role, %s
            FROM runs_raw
        ) t',
        sum_score_columns,
        make_score_columns
    );

    EXECUTE 'DROP TABLE IF EXISTS runs_enriched';
    EXECUTE maketable;
END $$;

CREATE INDEX idx_enriched
    ON runs_enriched (name, realm, class, spec);

/* Make character table */
DROP TABLE IF EXISTS characters;
CREATE TABLE characters AS
SELECT DISTINCT
    name, realm, class, spec, role, race, faction
FROM runs_raw;