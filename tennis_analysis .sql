-- 1. DATABASE TABLE CREATION & DATA IMPORTION

CREATE TABLE categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);
SELECT * FROM categories;
SELECT *
FROM categories
WHERE category_name = 'NA' OR category_name IS NULL;
UPDATE categories
SET category_name = TRIM(category_name);
SELECT category_id, COUNT(*)
FROM categories
GROUP BY category_id
HAVING COUNT(*) > 1;
SELECT COUNT(*) AS total_rows FROM categories;
SELECT DISTINCT category_name FROM categories;
CREATE TABLE competitions (
    competition_id VARCHAR(50) PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50),
    type VARCHAR(20),
    gender VARCHAR(10),
    category_id VARCHAR(50),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
SELECT * FROM competitions LIMIT 10;
SELECT competition_id, COUNT(*)
FROM competitions
GROUP BY competition_id
HAVING COUNT(*) > 1;
DELETE FROM competitions
WHERE competition_name IS NULL OR competition_name = 'NA';
UPDATE competitions
SET type = 'unknown'
WHERE type IS NULL OR type = 'NA';

UPDATE competitions
SET gender = 'unknown'
WHERE gender IS NULL OR gender = 'NA';
SELECT DISTINCT category_id
FROM competitions
WHERE category_id NOT IN (SELECT category_id FROM categories);
DELETE FROM competitions
WHERE category_id NOT IN (SELECT category_id FROM categories)
OR category_id IS NULL
OR category_id = 'NA';
SELECT DISTINCT parent_id
FROM competitions
WHERE parent_id IS NOT NULL
AND parent_id NOT IN (SELECT competition_id FROM competitions);

UPDATE competitions
SET parent_id = NULL
WHERE parent_id NOT IN (SELECT competition_id FROM competitions)
OR parent_id = 'NA';
UPDATE competitions
SET competition_name = TRIM(competition_name),
    type = LOWER(TRIM(type)),
    gender = LOWER(TRIM(gender));
SELECT COUNT(*) FROM competitions;

SELECT type, COUNT(*) 
FROM competitions 
GROUP BY type;

SELECT gender, COUNT(*) 
FROM competitions 
GROUP BY gender;

CREATE TABLE complexes (
    complex_id VARCHAR(50) PRIMARY KEY,
    complex_name VARCHAR(100) NOT NULL
);
SELECT * FROM complexes LIMIT 10;
SELECT complex_id, COUNT(*)
FROM complexes
GROUP BY complex_id
HAVING COUNT(*) > 1;
DELETE FROM complexes
WHERE complex_name IS NULL OR complex_name = 'NA';

UPDATE complexes
SET complex_name = TRIM(complex_name);

SELECT COUNT(*) FROM complexes;
SELECT DISTINCT complex_name FROM complexes;
CREATE TABLE venues (
    venue_id VARCHAR(50) PRIMARY KEY,
    venue_name VARCHAR(100),
    city_name VARCHAR(100),
    country_name VARCHAR(100),
    country_code CHAR(3),
    timezone VARCHAR(100),
    complex_id VARCHAR(50),
    FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
);
SELECT * FROM venues LIMIT 10;
SELECT venue_id, COUNT(*)
FROM venues
GROUP BY venue_id
HAVING COUNT(*) > 1;
DELETE FROM venues
WHERE venue_name IS NULL OR venue_name = 'NA';
UPDATE venues
SET city_name = 'Unknown'
WHERE city_name IS NULL OR city_name = 'NA';

UPDATE venues
SET country_name = 'Unknown'
WHERE country_name IS NULL OR country_name = 'NA';

UPDATE venues
SET timezone = 'Unknown'
WHERE timezone IS NULL OR timezone = 'NA';
UPDATE venues
SET city_name = 'Unknown'
WHERE city_name IS NULL OR city_name = 'NA';

UPDATE venues
SET country_name = 'Unknown'
WHERE country_name IS NULL OR country_name = 'NA';

UPDATE venues
SET timezone = 'Unknown'
WHERE timezone IS NULL OR timezone = 'NA';
UPDATE venues
SET country_code = UPPER(TRIM(country_code));
DELETE FROM venues
WHERE LENGTH(country_code) <> 3;
SELECT DISTINCT complex_id
FROM venues
WHERE complex_id NOT IN (SELECT complex_id FROM complexes);
DELETE FROM venues
WHERE complex_id NOT IN (SELECT complex_id FROM complexes)
OR complex_id IS NULL
OR complex_id = 'NA';
DELETE FROM venues
WHERE complex_id NOT IN (SELECT complex_id FROM complexes)
OR complex_id IS NULL
OR complex_id = 'NA';
UPDATE venues
SET venue_name = TRIM(venue_name),
    city_name = TRIM(city_name),
    country_name = TRIM(country_name),
    timezone = TRIM(timezone);
SELECT COUNT(*) FROM venues;

SELECT country_name, COUNT(*)
FROM venues
GROUP BY country_name;

SELECT complex_id, COUNT(*)
FROM venues
GROUP BY complex_id;

CREATE TABLE competitors (
    competitor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(100),
    country_code CHAR(3),
    abbreviation VARCHAR(10)
);
SELECT * FROM competitors LIMIT 10;
SELECT competitor_id, COUNT(*)
FROM competitors
GROUP BY competitor_id
HAVING COUNT(*) > 1;

UPDATE competitors
SET country_code = UPPER(TRIM(country_code));
UPDATE competitors
SET abbreviation = UPPER(TRIM(abbreviation));
UPDATE competitors
SET name = TRIM(name),
    country = TRIM(country);
SELECT COUNT(*) FROM competitors;

SELECT country, COUNT(*)
FROM competitors
GROUP BY country;
CREATE TABLE rankings (
    rank_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rank INT,
    movement INT,
    points INT,
    competitions_played INT,
    competitor_id VARCHAR(50),
    FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
);

DROP TABLE IF EXISTS rankings;
CREATE TABLE rankings (
    rank INT,
    movement INT,
    points INT,
    competitions_played INT,
    competitor_id VARCHAR(50),
    FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
);

-- 2. DATA CLEANING & ANALYTICAL QUERIES
SELECT COUNT(*) FROM categories;
SELECT COUNT(*) FROM competitions;
SELECT COUNT(*) FROM complexes;
SELECT COUNT(*) FROM venues;
SELECT COUNT(*) FROM competitors;
SELECT COUNT(*) FROM rankings;

-- Check NULLs
SELECT * FROM competitors WHERE competitor_id IS NULL;

-- Duplicate competitors
SELECT competitor_id, COUNT(*)
FROM competitors
GROUP BY competitor_id
HAVING COUNT(*) > 1;

SELECT c.name, r.points
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY r.points DESC
LIMIT 10;

SELECT AVG(points) AS avg_points
FROM rankings;

SELECT c.name, r.competitions_played
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY r.competitions_played DESC
LIMIT 10;

SELECT 
  CASE 
    WHEN rank BETWEEN 1 AND 10 THEN 'Top 10'
    WHEN rank BETWEEN 11 AND 50 THEN 'Top 11–50'
    WHEN rank BETWEEN 51 AND 100 THEN 'Top 51–100'
    ELSE 'Above 100'
  END AS rank_group,
  COUNT(*) AS players_count
FROM rankings
GROUP BY rank_group
ORDER BY players_count DESC;

SELECT 
  competitions_played,
  AVG(points) AS avg_points
FROM rankings
GROUP BY competitions_played
ORDER BY competitions_played;

SELECT 
  c.name,
  r.points,
  r.competitions_played,
  ROUND(r.points::DECIMAL / NULLIF(r.competitions_played, 0), 2) AS points_per_match
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY points_per_match DESC
LIMIT 10;

SELECT 
  c.name,
  r.rank,
  r.points,
  r.movement
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.movement BETWEEN -2 AND 2
ORDER BY r.points DESC;

SELECT 
  c.name,
  r.movement,
  r.rank
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
ORDER BY r.movement DESC
LIMIT 10;

SELECT 
  cat.name AS category,
  COUNT(comp.competitor_id) AS player_count
FROM competitors comp
JOIN categories cat ON comp.category_id = cat.category_id
GROUP BY cat.name
ORDER BY player_count DESC;

SELECT 
  country,
  COUNT(*) AS player_count
FROM competitors
GROUP BY country
ORDER BY player_count DESC;

SELECT 
  c.country,
  SUM(r.points) AS total_points
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
GROUP BY c.country
ORDER BY total_points DESC;

SELECT 
  cx.name AS complex_name,
  COUNT(v.venue_id) AS venue_count
FROM complexes cx
JOIN venues v ON cx.complex_id = v.complex_id
GROUP BY cx.name
ORDER BY venue_count DESC;

SELECT 
  cx.complex_name AS complex_name,
  COUNT(v.venue_id) AS venue_count
FROM complexes cx
JOIN venues v ON cx.complex_id = v.complex_id
GROUP BY cx.complex_name
ORDER BY venue_count DESC;

SELECT COUNT(*) AS missing_competitions
FROM rankings
WHERE competitions_played IS NULL OR competitions_played = 0;

CREATE VIEW top_players AS
SELECT 
  c.name,
  r.rank,
  r.points
FROM rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.rank <= 10;
SELECT * FROM top_players;

CREATE OR REPLACE VIEW top_players AS
SELECT 
  c.name,
  r.rank,
  r.points
FROM rankings r
JOIN competitors c 
  ON r.competitor_id = c.competitor_id
WHERE r.rank <= 10;
SELECT * FROM top_players;
SELECT MIN(rank), MAX(rank) FROM rankings;
SELECT COUNT(*) FROM rankings;
SELECT COUNT(rank) FROM rankings;

SELECT * FROM rankings;

SELECT MIN(rank), MAX(rank) FROM rankings;

CREATE OR REPLACE VIEW top_players AS
SELECT 
  c.name,
  r.rank,
  r.points
FROM rankings r
JOIN competitors c 
  ON r.competitor_id = c.competitor_id
WHERE r.rank <= 10;
SELECT * FROM top_players;

SELECT
  COUNT(*) AS total_players,
  AVG(points) AS avg_points,
  MAX(points) AS max_points,
  MIN(rank) AS best_rank
FROM rankings;



















