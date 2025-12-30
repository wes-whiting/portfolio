/* Make timestamp columns for character rating thresholds */
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS peak_rating float,
    ADD COLUMN IF NOT EXISTS ksc timestamptz,
    ADD COLUMN IF NOT EXISTS ksm timestamptz,
    ADD COLUMN IF NOT EXISTS ksh timestamptz,
    ADD COLUMN IF NOT EXISTS ksl timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_two_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_four_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS thirty_six_hundred timestamptz,
    ADD COLUMN IF NOT EXISTS title timestamptz;

UPDATE characters
SET
    peak_rating = subquery.peak_rating,
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
            name,
            realm,
            class,
            spec,
            min(timestamp) FILTER (WHERE total_score >= 1500) AS ksc,
            min(timestamp) FILTER (WHERE total_score >= 2000) AS ksm,
            min(timestamp) FILTER (WHERE total_score >= 2500) AS ksh,
            min(timestamp) FILTER (WHERE total_score >= 3000) AS ksl,
            min(timestamp) FILTER (WHERE total_score >= 3200) AS thirty_two_hundred,
            min(timestamp) FILTER (WHERE total_score >= 3400) AS thirty_four_hundred,
            min(timestamp) FILTER (WHERE total_score >= 3600) AS thirty_six_hundred,
            min(timestamp) FILTER (WHERE total_score >= 3804.8) AS title,
            max(total_score) AS peak_rating
         -- Title threshold for the season is 3804.8.
         FROM runs_enriched
         GROUP BY name, realm, class, spec
     ) as subquery
WHERE
    characters.name = subquery.name
  AND characters.realm = subquery.realm
  AND characters.class = subquery.class
  AND characters.spec = subquery.spec;