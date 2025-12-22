CREATE TABLE runs_enriched AS
SELECT name, dungeon, id, time, score,
	max(CASE WHEN dungeon_short = 'BREW' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'BREW',
	max(CASE WHEN dungeon = 'DFC' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'DFC',
	max(CASE WHEN dungeon = 'WORK' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'WORK',
	max(CASE WHEN dungeon = 'FLOOD' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'FLOOD',
	max(CASE WHEN dungeon = 'PSF' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'PSF',
	max(CASE WHEN dungeon = 'ML' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'ML',
	max(CASE WHEN dungeon = 'ROOK' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'ROOK',
	max(CASE WHEN dungeon = 'TOP' THEN score ELSE 0 END) 
		OVER (
			PARTITION BY id, name, realm
			ORDER BY time
			ROWS BETWEEN unbounded preceding AND current row
	) AS 'TOP'
FROM runs_raw;