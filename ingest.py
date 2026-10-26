"""
Santander Cycles ingestion: pull live dock data from the TfL API,
save the raw response untouched, then load a tidy snapshot into DuckDB.

Run once:        python ingest.py
Run every 5 min: python ingest.py --loop
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

API_URL = "https://api.tfl.gov.uk/BikePoint"
RAW_DIR = Path("data/raw")
DB_PATH = "data/bikes.duckdb"
INTERVAL_SECONDS = 300  # 5 minutes


def fetch_bikepoints():
    """Call the TfL API and return the parsed JSON (a list of docking stations)."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()  # stop with a clear error if the API fails
    return response.json()


def save_raw(data, fetched_at):
    """Store the untouched API response so we can always reprocess it later."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"bikepoints_{fetched_at:%Y%m%dT%H%M%SZ}.json"
    path.write_text(json.dumps(data))
    return path


def to_rows(data, fetched_at):
    """Flatten the nested JSON into one simple row per station."""
    rows = []
    for station in data:
        # TfL stores most values as a list of {"key": ..., "value": ...} pairs
        props = {p["key"]: p["value"] for p in station.get("additionalProperties", [])}
        rows.append(
            (
                fetched_at,
                station["id"],
                station["commonName"],
                station["lat"],
                station["lon"],
                int(props.get("NbBikes", 0)),
                int(props.get("NbEmptyDocks", 0)),
                int(props.get("NbDocks", 0)),
            )
        )
    return rows


def load_to_duckdb(rows):
    """Append this snapshot to the local database."""
    con = duckdb.connect(DB_PATH)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS station_snapshots (
            fetched_at   TIMESTAMP,
            station_id   VARCHAR,
            station_name VARCHAR,
            lat          DOUBLE,
            lon          DOUBLE,
            bikes        INTEGER,
            empty_docks  INTEGER,
            total_docks  INTEGER
        )
        """
    )
    con.executemany(
        "INSERT INTO station_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows
    )
    con.close()


def run_once():
    fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)
    data = fetch_bikepoints()
    raw_path = save_raw(data, fetched_at)
    rows = to_rows(data, fetched_at)
    load_to_duckdb(rows)
    print(f"{fetched_at:%H:%M:%S} saved {len(rows)} stations -> {raw_path.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="repeat every 5 minutes")
    args = parser.parse_args()

    Path("data").mkdir(exist_ok=True)

    if not args.loop:
        run_once()
        return

    while True:
        try:
            run_once()
        except Exception as error:  # keep running if one call fails
            print(f"Run failed, will retry next cycle: {error}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
