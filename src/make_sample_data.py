"""Generate realistic synthetic artifacts so the app runs with zero external deps.

This is the demo safety net: if the real BigQuery/Colab artifacts aren't present,
the app calls this to produce plausible London-shaped station features + a benchmark
placeholder. Replace data/station_features.parquet with the real Colab output for the
final submission.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import config

# A spread of real-ish central London station coordinates to anchor the map.
_ANCHORS = [
    ("Hyde Park Corner", 51.5030, -0.1527),
    ("King's Cross", 51.5308, -0.1238),
    ("Waterloo Station", 51.5033, -0.1145),
    ("Shoreditch High St", 51.5234, -0.0757),
    ("Canary Wharf", 51.5054, -0.0235),
    ("Soho Square", 51.5155, -0.1322),
    ("Victoria Station", 51.4952, -0.1441),
    ("Liverpool Street", 51.5178, -0.0823),
    ("Southbank Centre", 51.5065, -0.1160),
    ("Notting Hill Gate", 51.5090, -0.1962),
    ("Angel, Islington", 51.5322, -0.1058),
    ("London Bridge", 51.5049, -0.0863),
]


def generate(n_stations: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for sid in range(n_stations):
        base_name, blat, blon = _ANCHORS[sid % len(_ANCHORS)]
        lat = blat + rng.normal(0, 0.012)
        lon = blon + rng.normal(0, 0.018)
        name = f"{base_name} #{sid // len(_ANCHORS) + 1}"
        docks = int(rng.integers(14, 42))
        # station "personality": commuter-out (residential), commuter-in (office), or leisure
        kind = rng.choice(["residential", "office", "leisure"], p=[0.4, 0.4, 0.2])
        pop = rng.uniform(0.6, 1.8)  # how busy the station is
        for how in range(config.HOURS_IN_WEEK):
            day, hour = how // 24, how % 24
            weekend = day >= 5
            rush_am = 7 <= hour <= 9
            rush_pm = 17 <= hour <= 19
            demand = 0.6 + (0.0 if weekend else 0.0)
            if rush_am:
                demand = 3.2
            elif rush_pm:
                demand = 3.0
            elif 10 <= hour <= 16:
                demand = 1.6
            elif hour <= 5 or hour >= 23:
                demand = 0.25
            demand *= pop * (0.7 if weekend else 1.0)

            # direction of flow depends on station kind + time of day
            if kind == "residential":
                lean = 1.0 if rush_am else (-0.9 if rush_pm else 0.0)
            elif kind == "office":
                lean = -1.0 if rush_am else (0.9 if rush_pm else 0.0)
            else:
                lean = rng.normal(0, 0.3)

            deps = max(0.0, demand * (1 + 0.5 * lean) + rng.normal(0, 0.25))
            arrs = max(0.0, demand * (1 - 0.5 * lean) + rng.normal(0, 0.25))
            rows.append(
                {
                    "station_id": sid,
                    "station_name": name,
                    "lat": lat,
                    "lon": lon,
                    "docks_count": docks,
                    "hour_of_week": how,
                    "mean_departures": round(deps, 3),
                    "mean_arrivals": round(arrs, 3),
                    "net_flow": round(deps - arrs, 3),
                    "volatility": round(abs(rng.normal(0.4, 0.2)), 3),
                }
            )
    return pd.DataFrame(rows)


def sample_benchmark() -> dict:
    """Placeholder benchmark. Overwritten by the real Colab measurement."""
    n = 6_500_000
    cpu = 41.8
    gpu = 2.4
    return {
        "n_trips": n,
        "cpu_seconds": cpu,
        "gpu_seconds": gpu,
        "speedup": round(cpu / gpu, 1),
        "rows_per_sec_cpu": int(n / cpu),
        "rows_per_sec_gpu": int(n / gpu),
        "gpu_name": "NVIDIA T4 (Colab)",
        "generated_at": "synthetic-placeholder",
        "is_synthetic": True,
    }


def write(features_path=config.FEATURES_PATH, benchmark_path=config.BENCHMARK_PATH):
    features_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_parquet(features_path, index=False)
    with open(benchmark_path, "w") as fh:
        json.dump(sample_benchmark(), fh, indent=2)
    return df


if __name__ == "__main__":
    df = write()
    print(f"Wrote {len(df):,} feature rows to {config.FEATURES_PATH}")
    print(f"Wrote benchmark to {config.BENCHMARK_PATH}")
