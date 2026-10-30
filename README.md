# London Bike Dock Availability Pipeline

## The question
Which Santander Cycles docking stations run empty or full, and at what times of day?

## Who it helps
A commuter deciding where to pick up or drop off a bike, and a transport analyst
looking at where bikes need rebalancing.

## How it works (current stage)
1. `ingest.py` calls the TfL BikePoint API every 5 minutes.
2. The untouched response is saved to `data/raw/` (so I can always reprocess it).
3. A flattened snapshot is appended to a local DuckDB table, `station_snapshots`.

## Run it
```
pip install -r requirements.txt
python ingest.py          # one run
python ingest.py --loop   # every 5 minutes
```

## Design decisions (fill in as you go)
- Why batch every 5 minutes instead of streaming?
- Why DuckDB for the first version?
- What happens if the API is down?

## Problems I hit and how I fixed them
(Add real ones here as they happen. This section is gold in interviews.)

## Data quality checks
`python checks.py` tests the database after collection:

| Check | Type |
|---|---|
| No negative bike or dock counts | FAIL if broken |
| No missing station id or name | FAIL if broken |
| No duplicate rows in a snapshot | FAIL if broken |
| Bikes + empty docks never exceed total docks | WARN |
| Coordinates fall inside London | WARN |
| No gaps over 10 minutes between snapshots | WARN |

Current result: all integrity checks pass. The gap check reports 4 gaps, which
are the periods when the collector was not running.

## Known limitations
- The collector runs on my laptop and only collects while it is awake, so there
  are gaps and no data yet for early mornings or the evening rush.
- Timestamps are stored in UTC. London changed from summer time to GMT on
  25 Oct 2026, so earlier data is one hour off from London clock time.
- The station count varies slightly between snapshots (798 to 801), so queries
  never assume a fixed number of stations.
- With only a few days of data, I do not claim any time-of-day patterns yet.

## Problems I hit and how I fixed them
- **Wrong folder, wrong database.** Running a script from a different folder
  created a second, tiny database inside OneDrive. I fixed it by opening the
  editor on the project folder and checking the terminal path before running.
- **A pattern that was not one.** The first hour-of-day table made mornings
  look emptier than afternoons. Grouping by day as well showed the difference
  came from which days I had collected, not from the time of day.

## Roadmap
- [ ] Run the collector for 2+ weeks
- [ ] SQL models: hourly averages, "empty/full" flags per station
- [x] Data quality checks (missing stations, impossible values)
- [ ] Scheduling (cron, then Airflow or Prefect)
- [ ] Streamlit dashboard
- [ ] Docker
- [ ] Move storage and database to a free cloud tier
