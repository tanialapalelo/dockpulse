"""Turn flow features into an actionable, explainable risk score.

Pure pandas/numpy so it runs instantly in the Streamlit app for whatever
hour-of-week the dispatcher selects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def score(features: pd.DataFrame, hour_of_week: int, docks_default: int = 20) -> pd.DataFrame:
    """Score every station for a given hour-of-week.

    Returns one row per station with a 0-100 risk score, a status label
    (EMPTY_RISK / FULL_RISK / OK) and the concrete action (bikes to move).
    """
    df = features[features["hour_of_week"] == hour_of_week].copy()
    if df.empty:
        return df.assign(risk=[], status=[], bikes_to_move=[])

    if "docks_count" not in df.columns:
        df["docks_count"] = docks_default
    df["docks_count"] = df["docks_count"].replace(0, docks_default).fillna(docks_default)

    predicted = df["net_flow"].to_numpy()
    docks = df["docks_count"].to_numpy()
    vol = df.get("volatility", pd.Series(np.zeros(len(df)))).to_numpy()

    # pressure = expected 1h net flow relative to capacity
    pressure = np.abs(predicted) / np.maximum(docks, 1)
    base_risk = 100.0 * pressure / config.PRESSURE_FULL_SCALE
    # volatile stations are less predictable -> nudge risk up
    vol_factor = 1.0 + config.VOLATILITY_BOOST * (vol / (np.abs(predicted) + 1e-6)).clip(0, 1)
    risk = np.clip(base_risk * vol_factor, 0, 100)

    status = np.where(
        risk < config.RISK_ALERT_THRESHOLD,
        "OK",
        np.where(predicted > 0, "EMPTY_RISK", "FULL_RISK"),
    )

    df["risk"] = np.round(risk, 1)
    df["status"] = status
    # net outflow (positive) => bikes leave => send bikes IN; sign kept for readability
    df["bikes_to_move"] = np.round(predicted).astype(int)
    df["predicted_net_flow"] = np.round(predicted, 2)

    return df.sort_values("risk", ascending=False).reset_index(drop=True)


def alerts(scored: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """The ranked 'rebalance now' list the dispatcher acts on."""
    hot = scored[scored["status"] != "OK"]
    return hot.head(top_n)
