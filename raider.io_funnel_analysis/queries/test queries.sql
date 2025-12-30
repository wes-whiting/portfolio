SELECT count(*) FROM(
    SELECT DISTINCT name, realm FROM characters);

SELECT count(*) FROM(
    SELECT DISTINCT name, realm, class FROM characters);