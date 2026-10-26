"""
Your first SQL queries on the bike data.
Run in a SECOND terminal while the collector keeps running:  python query.py
"""

import duckdb

con = duckdb.connect("data/bikes.duckdb", read_only=True)


def show(title, sql):
    print(f"\n=== {title} ===")
    print(con.sql(sql))


# 1. How much data do we have so far?
#    COUNT(*) counts rows. COUNT(DISTINCT ...) counts unique values.
show(
    "How much data so far",
    """
    SELECT COUNT(*)                    AS total_rows,
           COUNT(DISTINCT fetched_at)  AS snapshots
    FROM station_snapshots
    """,
)

# 2. Look at a few raw rows. SELECT * means "all columns", LIMIT keeps it short.
show(
    "First 5 rows",
    """
    SELECT *
    FROM station_snapshots
    LIMIT 5
    """,
)

# 3. Which stations have the FEWEST bikes right now?
#    WHERE filters rows, ORDER BY sorts them, LIMIT keeps the top 10.
#    The sub-query in brackets finds the most recent snapshot time.
show(
    "Emptiest stations in the latest snapshot",
    """
    SELECT station_name, bikes, empty_docks, total_docks
    FROM station_snapshots
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM station_snapshots)
    ORDER BY bikes ASC
    LIMIT 10
    """,
)
