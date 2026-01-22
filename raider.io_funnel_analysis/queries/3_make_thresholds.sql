/* Make timestamp columns for character rating thresholds */
ALTER TABLE characters
    ADD COLUMN IF NOT EXISTS peak_rating float,
    ADD COLUMN IF NOT EXISTS time_0 timestamptz,
    ADD COLUMN IF NOT EXISTS time_1500 timestamptz,
    ADD COLUMN IF NOT EXISTS time_2000 timestamptz,
    ADD COLUMN IF NOT EXISTS time_2500 timestamptz,
    ADD COLUMN IF NOT EXISTS time_3000 timestamptz,
    ADD COLUMN IF NOT EXISTS time_3200 timestamptz,
    ADD COLUMN IF NOT EXISTS time_3400 timestamptz,
    ADD COLUMN IF NOT EXISTS time_3600 timestamptz,
    ADD COLUMN IF NOT EXISTS time_title timestamptz;

UPDATE characters
SET
    peak_rating = subquery.peak_rating,
    time_0 = subquery.time_0,
    time_1500 = subquery.time_1500,
    time_2000 = subquery.time_2000,
    time_2500 = subquery.time_2500,
    time_3000 = subquery.time_3000,
    time_3200 = subquery.time_3200,
    time_3400 = subquery.time_3400,
    time_3600 = subquery.time_3600,
    time_title = subquery.time_title
FROM (
        SELECT
            name,
            realm,
            class,
            spec,
            min(completed_at) FILTER (WHERE total_score > 0) AS time_0,
            min(completed_at) FILTER (WHERE total_score >= 1500) AS time_1500,
            min(completed_at) FILTER (WHERE total_score >= 2000) AS time_2000,
            min(completed_at) FILTER (WHERE total_score >= 2500) AS time_2500,
            min(completed_at) FILTER (WHERE total_score >= 3000) AS time_3000,
            min(completed_at) FILTER (WHERE total_score >= 3200) AS time_3200,
            min(completed_at) FILTER (WHERE total_score >= 3400) AS time_3400,
            min(completed_at) FILTER (WHERE total_score >= 3600) AS time_3600,
            min(completed_at) FILTER (WHERE total_score >= 3804.8) AS time_title,
            -- Title threshold for TWW season 2 is 3804.8. https://raider.io/mythic-plus/cutoffs/season-tww-2/us
            max(total_score) AS peak_rating
         FROM runs_enriched
         GROUP BY name, realm, class, spec
     ) as subquery
WHERE
    characters.name = subquery.name
  AND characters.realm = subquery.realm
  AND characters.class = subquery.class
  AND characters.spec = subquery.spec;