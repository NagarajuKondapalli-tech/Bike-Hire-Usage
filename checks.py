"""
Data quality checks for the bike dock database.

Run:  python checks.py

Each check counts "bad" rows. 0 means PASS.
FAIL = the data is broken. WARN = worth knowing about, not necessarily wrong.
"""

import sys

import duckdb

con = duckdb.connect("data/bikes.duckdb", read_only=True)

CHECKS = [
    (
        "No negative bike or dock counts",
        "FAIL",
        """
        SELECT COUNT(*) FROM station_snapshots
        WHERE bikes < 0 OR empty_docks < 0 OR total_docks < 0
        """,
    ),
    (
        "No missing station id or name",
        "FAIL",
        """
        SELECT COUNT(*) FROM station_snapshots
        WHERE station_id IS NULL OR station_name IS NULL
        """,
    ),
    (
        "No duplicate rows (same station in the same snapshot)",
        "FAIL",
        """
        SELECT COUNT(*) FROM (
            SELECT fetched_at, station_id
            FROM station_snapshots
            GROUP BY fetched_at, station_id
            HAVING COUNT(*) > 1
        )
        """,
    ),
    (
        "Bikes + empty docks never exceed total docks",
        "WARN",
        """
        SELECT COUNT(*) FROM station_snapshots
        WHERE bikes + empty_docks > total_docks
        """,
    ),
    (
        "Coordinates look like London (lat 51-52, lon -1 to 0.5)",
        "WARN",
        """
        SELECT COUNT(*) FROM station_snapshots
        WHERE lat NOT BETWEEN 51 AND 52 OR lon NOT BETWEEN -1 AND 0.5
        """,
    ),
    (
        "No gaps longer than 10 minutes between snapshots",
        "WARN",
        """
        WITH t AS (SELECT DISTINCT fetched_at FROM station_snapshots),
             g AS (SELECT fetched_at,
                          LAG(fetched_at) OVER (ORDER BY fetched_at) AS prev
                   FROM t)
        SELECT COUNT(*) FROM g
        WHERE prev IS NOT NULL
          AND date_diff('minute', prev, fetched_at) > 10
        """,
    ),
]

any_fail = False
for name, severity, sql in CHECKS:
    bad = con.execute(sql).fetchall()[0][0]
    status = "PASS" if bad == 0 else severity
    print(f"[{status:4}] {name}  (bad: {bad})")
    if bad and severity == "FAIL":
        any_fail = True

print("\nStations per snapshot (min / max):")
print(
    con.sql(
        """
        SELECT MIN(n) AS min_stations, MAX(n) AS max_stations FROM (
            SELECT fetched_at, COUNT(*) AS n
            FROM station_snapshots
            GROUP BY fetched_at
        )
        """
    )
)

sys.exit(1 if any_fail else 0)
