import duckdb

con = duckdb.connect("data/bikes.duckdb", read_only=True)

# ---- EDIT THE SQL BELOW ----
query = """
SELECT station_name,
       COUNT(*) AS snapshots_seen,
       SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) AS times_empty,
       ROUND(100.0 * SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_empty
FROM station_snapshots
GROUP BY station_name
ORDER BY pct_empty DESC
LIMIT 10
"""
query = """
SELECT station_name,
       COUNT(*) AS snapshots_seen,
       ROUND(100.0 * SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_empty,
       ROUND(AVG(total_docks - bikes - empty_docks), 1) AS avg_unavailable_docks
FROM station_snapshots
GROUP BY station_name
ORDER BY pct_empty DESC
LIMIT 10
"""
query = """
SELECT EXTRACT(hour FROM fetched_at) AS hour_utc,
       COUNT(DISTINCT fetched_at) AS snapshots,
       ROUND(AVG(bikes), 1) AS avg_bikes_per_station,
       ROUND(100.0 * SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_empty
FROM station_snapshots
GROUP BY hour_utc
ORDER BY hour_utc
"""
query = """
SELECT CAST(fetched_at AS DATE) AS day,
       EXTRACT(hour FROM fetched_at) AS hour_utc,
       COUNT(DISTINCT fetched_at) AS snapshots,
       ROUND(100.0 * SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_empty
FROM station_snapshots
GROUP BY day, hour_utc
ORDER BY day, hour_utc
"""
query = """
SELECT fetched_at, COUNT(*) AS stations, SUM(CASE WHEN bikes = 0 THEN 1 ELSE 0 END) AS empty
FROM station_snapshots
WHERE CAST(fetched_at AS DATE) = '2026-10-22' AND EXTRACT(hour FROM fetched_at) = 10
GROUP BY fetched_at
ORDER BY fetched_at
"""
# ---- END OF SQL ----

print(con.sql(query))