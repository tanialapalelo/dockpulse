"""Central configuration for DockPulse.

Keeping constants in one place makes the pipeline, the app, and the notebook agree
on table names, thresholds, and file paths.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FEATURES_PATH = DATA_DIR / "station_features.parquet"
BENCHMARK_PATH = DATA_DIR / "benchmark.json"
RAW_TRIPS_PATH = DATA_DIR / "raw_trips.parquet"

# ---------------------------------------------------------------------------
# BigQuery source (London bike-share — large public dataset)
# ---------------------------------------------------------------------------
BQ_TRIPS_TABLE = "bigquery-public-data.london_bicycles.cycle_hire"
BQ_STATIONS_TABLE = "bigquery-public-data.london_bicycles.cycle_stations"
# Bound the extract so we stay inside the BigQuery free tier (1 TB/month).
# Widen this range in the notebook if you have quota to spare (bigger = better GPU story).
BQ_START_DATE = "2016-06-01"
BQ_END_DATE = "2016-09-01"

# ---------------------------------------------------------------------------
# Risk model
# ---------------------------------------------------------------------------
HOURS_IN_WEEK = 168               # 7 days * 24 hours
PRESSURE_FULL_SCALE = 0.35        # net_flow/docks at which risk saturates to ~100
RISK_ALERT_THRESHOLD = 55         # >= this risk score => it's an alert
VOLATILITY_BOOST = 0.25           # how much per-station volatility inflates risk

# Default "current" moment shown when the app opens: Friday 18:00 (evening rush).
DEFAULT_HOUR_OF_WEEK = 4 * 24 + 18

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def hour_of_week_label(how: int) -> str:
    """Turn an hour-of-week index (0-167) into e.g. 'Fri 18:00'."""
    day = (how // 24) % 7
    hour = how % 24
    return f"{DAY_NAMES[day]} {hour:02d}:00"
