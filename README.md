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

## Roadmap
- [ ] Run the collector for 2+ weeks
- [ ] SQL models: hourly averages, "empty/full" flags per station
- [ ] Data quality checks (missing stations, impossible values)
- [ ] Scheduling (cron, then Airflow or Prefect)
- [ ] Streamlit dashboard
- [ ] Docker
- [ ] Move storage and database to a free cloud tier
