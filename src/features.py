"""Feature engineering — the GPU-accelerated heart of DockPulse.

`build_features` is written against the *shared* pandas/cuDF API so the SAME function
runs on a pandas DataFrame (CPU) or a cuDF DataFrame (GPU). That is what makes the
benchmark honest: identical logic, only the dataframe library changes.

Input: raw trips with columns
    start_station_id, start_station_name, start_lat, start_lon,
    end_station_id,   end_station_name,   end_lat,   end_lon,
    start_date (datetime), end_date (datetime)

Output: one row per (station_id, hour_of_week) with mean departures, mean arrivals,
net flow and volatility — a compact table the app can score instantly.
"""
from __future__ import annotations


def _hour_of_week(dt_series):
    """Vectorised hour-of-week (0-167). Works on pandas and cuDF datetime series."""
    return dt_series.dt.dayofweek * 24 + dt_series.dt.hour


def _events(df, station_col, name_col, lat_col, lon_col, time_col, kind, xp):
    """Build a per-(station, hour_of_week, date) event count table for one side of a trip.

    kind is 'dep' (departures) or 'arr' (arrivals). `xp` is the dataframe module
    (pandas or cudf) so we can construct the intermediate frame in the right library.
    """
    ev = xp.DataFrame(
        {
            "station_id": df[station_col],
            "station_name": df[name_col],
            "lat": df[lat_col],
            "lon": df[lon_col],
            "hour_of_week": _hour_of_week(df[time_col]),
            # normalise to a calendar date so we can average across weeks
            "date": df[time_col].dt.floor("D"),
        }
    )
    ev = ev.dropna(subset=["station_id"])
    # count events per station/hour-of-week/date (one row per station per day per hour bucket)
    counts = (
        ev.groupby(["station_id", "hour_of_week", "date"]).size().reset_index()
    )
    counts = counts.rename(columns={counts.columns[-1]: f"n_{kind}"})
    meta = (
        ev.groupby("station_id")
        .agg({"station_name": "min", "lat": "mean", "lon": "mean"})
        .reset_index()
    )
    return counts, meta


def build_features(df, xp=None):
    """Aggregate raw trips into per-(station, hour_of_week) flow features.

    Parameters
    ----------
    df : pandas.DataFrame | cudf.DataFrame
    xp : module, optional
        The dataframe library matching ``df`` (pandas or cudf). If omitted it is
        inferred from the dataframe's module, so callers usually don't pass it.
    """
    if xp is None:
        xp = _infer_xp(df)

    dep_counts, dep_meta = _events(
        df, "start_station_id", "start_station_name", "start_lat", "start_lon",
        "start_date", "dep", xp,
    )
    arr_counts, arr_meta = _events(
        df, "end_station_id", "end_station_name", "end_lat", "end_lon",
        "end_date", "arr", xp,
    )

    # Average event counts across the observed dates -> typical departures/arrivals
    dep_mean = (
        dep_counts.groupby(["station_id", "hour_of_week"])["n_dep"].mean().reset_index()
        .rename(columns={"n_dep": "mean_departures"})
    )
    dep_std = (
        dep_counts.groupby(["station_id", "hour_of_week"])["n_dep"].std().reset_index()
        .rename(columns={"n_dep": "dep_volatility"})
    )
    arr_mean = (
        arr_counts.groupby(["station_id", "hour_of_week"])["n_arr"].mean().reset_index()
        .rename(columns={"n_arr": "mean_arrivals"})
    )

    feats = dep_mean.merge(arr_mean, on=["station_id", "hour_of_week"], how="outer")
    feats = feats.merge(dep_std, on=["station_id", "hour_of_week"], how="left")
    feats = feats.fillna(0)

    feats["net_flow"] = feats["mean_departures"] - feats["mean_arrivals"]
    feats["volatility"] = feats["dep_volatility"]

    # attach station geo/name (prefer departure metadata, fall back to arrival)
    meta = dep_meta.merge(
        arr_meta, on="station_id", how="outer", suffixes=("", "_arr")
    )
    meta["station_name"] = meta["station_name"].fillna(meta["station_name_arr"])
    meta["lat"] = meta["lat"].fillna(meta["lat_arr"])
    meta["lon"] = meta["lon"].fillna(meta["lon_arr"])
    meta = meta[["station_id", "station_name", "lat", "lon"]]

    feats = feats.merge(meta, on="station_id", how="left")
    feats = feats[[
        "station_id", "station_name", "lat", "lon", "hour_of_week",
        "mean_departures", "mean_arrivals", "net_flow", "volatility",
    ]]
    return feats


def _infer_xp(df):
    module = type(df).__module__
    if module.startswith("cudf"):
        import cudf  # noqa: WPS433 (local import — cudf only exists on GPU)
        return cudf
    import pandas as pd
    return pd
