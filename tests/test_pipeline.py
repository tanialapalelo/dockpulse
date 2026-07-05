"""Fast unit tests — run with: python -m pytest -q  (or python tests/test_pipeline.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, score_risk  # noqa: E402
from src.features import build_features  # noqa: E402


def _toy_trips() -> pd.DataFrame:
    """Two stations, one hour bucket (Mon 08:00), across 2 days.

    Station A: 4 departures, 0 arrivals -> net +2/day -> emptying.
    Station B: 0 departures, 4 arrivals -> net -2/day -> filling.
    """
    mon_8 = pd.Timestamp("2016-06-06 08:15")   # Monday
    mon_8b = pd.Timestamp("2016-06-13 08:20")  # next Monday
    rows = []
    for t in (mon_8, mon_8b):
        for _ in range(2):  # 2 departures/day from A -> B
            rows.append(dict(
                start_station_id=1, start_station_name="A", start_lat=51.5, start_lon=-0.1,
                end_station_id=2, end_station_name="B", end_lat=51.6, end_lon=-0.2,
                start_date=t, end_date=t + pd.Timedelta(minutes=10),
            ))
    return pd.DataFrame(rows)


def test_build_features_net_flow():
    feats = build_features(_toy_trips())
    how = 0 * 24 + 8  # Monday 08:00
    a = feats[(feats.station_id == 1) & (feats.hour_of_week == how)].iloc[0]
    b = feats[(feats.station_id == 2) & (feats.hour_of_week == how)].iloc[0]
    # A: 2 departures/day averaged -> 2 ; 0 arrivals -> net +2
    assert np.isclose(a.mean_departures, 2.0)
    assert np.isclose(a.mean_arrivals, 0.0)
    assert a.net_flow > 0                      # emptying
    # B: 0 departures, 2 arrivals -> net -2
    assert np.isclose(b.mean_arrivals, 2.0)
    assert b.net_flow < 0                      # filling


def test_score_status_labels():
    feats = build_features(_toy_trips())
    feats["docks_count"] = 5
    how = 0 * 24 + 8
    scored = score_risk.score(feats, how)
    by_id = {r.station_id: r for _, r in scored.iterrows()}
    assert by_id[1].status == "EMPTY_RISK"     # net outflow
    assert by_id[2].status == "FULL_RISK"      # net inflow
    assert 0 <= by_id[1].risk <= 100


def test_score_empty_hour_is_safe():
    feats = build_features(_toy_trips())
    scored = score_risk.score(feats, hour_of_week=100)  # no data this hour
    assert len(scored) == 0                    # returns empty, does not raise


if __name__ == "__main__":
    test_build_features_net_flow()
    test_score_status_labels()
    test_score_empty_hour_is_safe()
    print("All tests passed ✅")
