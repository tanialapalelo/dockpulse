"""DockPulse — bike-share rebalancing early-warning dashboard.

Serving layer: loads precomputed (GPU-built) features, scores risk for the selected
hour on the fly, and shows the map + ranked alerts + benchmark + Gemini briefing.
Runs on CPU; deploys free to Streamlit Community Cloud.
"""
from __future__ import annotations

import json
import os

import pandas as pd
import pydeck as pdk
import streamlit as st

from src import config, score_risk
from src.gemini_brief import brief

st.set_page_config(page_title="DockPulse", page_icon="🚲", layout="wide")

# Bridge Streamlit Cloud secrets -> env vars so src/gemini_brief.py (Streamlit-agnostic) sees them.
for _k in ("GEMINI_API_KEY", "GEMINI_MODEL"):
    try:
        if _k in st.secrets and not os.environ.get(_k):
            os.environ[_k] = str(st.secrets[_k])
    except Exception:
        pass

STATUS_COLOR = {
    "EMPTY_RISK": [214, 40, 40],     # red   — bikes leaving, station emptying
    "FULL_RISK": [29, 111, 214],     # blue  — bikes arriving, docks filling
    "OK": [120, 190, 120],           # green — balanced
}


@st.cache_data(show_spinner=False)
def load_features() -> pd.DataFrame:
    """Load GPU-built features; fall back to synthetic data so the app always runs."""
    if config.FEATURES_PATH.exists():
        return pd.read_parquet(config.FEATURES_PATH)
    from src.make_sample_data import write
    return write()


@st.cache_data(show_spinner=False)
def load_benchmark() -> dict:
    if config.BENCHMARK_PATH.exists():
        with open(config.BENCHMARK_PATH) as fh:
            return json.load(fh)
    from src.make_sample_data import sample_benchmark
    return sample_benchmark()


def risk_layer(scored: pd.DataFrame) -> pdk.Layer:
    df = scored.copy()
    df["color"] = df["status"].map(STATUS_COLOR)
    df["radius"] = 60 + df["risk"] * 4
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
        opacity=0.75,
    )


def main() -> None:
    features = load_features()
    bench = load_benchmark()

    # ---- Sidebar controls -------------------------------------------------
    st.sidebar.title("🚲 DockPulse")
    st.sidebar.caption("Rebalancing early-warning for bike-share ops")
    how = st.sidebar.slider(
        "Hour of week", 0, config.HOURS_IN_WEEK - 1,
        value=config.DEFAULT_HOUR_OF_WEEK,
        help="Pick the moment the dispatcher is planning for.",
    )
    st.sidebar.markdown(f"### 🕒 {config.hour_of_week_label(how)}")
    top_n = st.sidebar.slider("Alerts to show", 3, 20, 10)
    if bench.get("is_synthetic"):
        st.sidebar.warning("Showing synthetic data. Drop the real Colab artifacts into `data/` for live numbers.")

    scored = score_risk.score(features, how)
    alerts = score_risk.alerts(scored, top_n)

    # ---- Header + KPIs ----------------------------------------------------
    st.title("DockPulse — will your docks run empty next hour?")
    st.caption(
        "A bike-share dispatcher's early-warning board. GPU-accelerated pipeline over "
        f"{bench.get('n_trips', 0):,} trips (BigQuery → RAPIDS cuDF → Gemini)."
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Stations at risk", int((scored["status"] != "OK").sum()))
    k2.metric("Emptying 🔴", int((scored["status"] == "EMPTY_RISK").sum()))
    k3.metric("Filling 🔵", int((scored["status"] == "FULL_RISK").sum()))
    k4.metric("GPU speed-up", f"{bench.get('speedup', 0)}×",
              help=f"cuDF {bench.get('gpu_seconds')}s vs pandas {bench.get('cpu_seconds')}s on {bench.get('gpu_name')}")

    left, right = st.columns([3, 2])

    # ---- Map --------------------------------------------------------------
    with left:
        st.subheader("Risk map")
        if len(scored):
            view = pdk.ViewState(
                latitude=float(scored["lat"].mean()),
                longitude=float(scored["lon"].mean()),
                zoom=11.5, pitch=0,
            )
            st.pydeck_chart(
                pdk.Deck(
                    layers=[risk_layer(scored)],
                    initial_view_state=view,
                    map_style=None,
                    tooltip={"text": "{station_name}\nrisk {risk} · {status}"},
                ),
                use_container_width=True,
            )
        st.caption("🔴 emptying · 🔵 filling · 🟢 balanced. Dot size = risk.")

    # ---- Ops briefing (Gemini) -------------------------------------------
    with right:
        st.subheader("🧠 Gemini ops briefing")
        text, source = brief(alerts, config.hour_of_week_label(how))
        st.markdown(text)
        badge = "✅ Gemini" if source == "gemini" else "📝 Template (no API key)"
        st.caption(f"Source: {badge}")

    # ---- Ranked alerts ----------------------------------------------------
    st.subheader("🚨 Rebalance now — ranked alerts")
    if alerts.empty:
        st.success("Network balanced this hour — no crews needed.")
    else:
        show = alerts[["station_name", "status", "risk", "predicted_net_flow", "bikes_to_move", "docks_count"]].copy()
        show.columns = ["Station", "Status", "Risk", "Net flow (1h)", "Bikes to move", "Docks"]
        st.dataframe(show, use_container_width=True, hide_index=True)

    # ---- Acceleration proof ----------------------------------------------
    st.subheader("⚡ Acceleration proof — CPU vs GPU")
    b1, b2 = st.columns([2, 3])
    with b1:
        st.metric("pandas (CPU)", f"{bench.get('cpu_seconds')}s")
        st.metric("cuDF (GPU)", f"{bench.get('gpu_seconds')}s")
        st.metric("Time-to-insight", f"{bench.get('speedup')}× faster")
    with b2:
        chart_df = pd.DataFrame(
            {"engine": ["pandas (CPU)", "cuDF (GPU)"],
             "seconds": [bench.get("cpu_seconds", 0), bench.get("gpu_seconds", 0)]}
        ).set_index("engine")
        st.bar_chart(chart_df, horizontal=True)
        st.caption(
            f"Same feature-engineering code over {bench.get('n_trips', 0):,} trips. "
            f"{bench.get('rows_per_sec_gpu', 0):,} rows/s on {bench.get('gpu_name')} "
            f"vs {bench.get('rows_per_sec_cpu', 0):,} rows/s on CPU."
        )


if __name__ == "__main__":
    main()
