CREATE TABLE characters AS
SELECT DISTINCT id, Name, Realm, Class
FROM runs_raw;

CREATE TABLE dungeons AS
SELECT DISTINCT Dungeon, dungeon_short
FROM runs_raw;