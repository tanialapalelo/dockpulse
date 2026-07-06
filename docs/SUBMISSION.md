# DockPulse — Submission Brief

*Paste this into the Hack2Skill submission form's "brief description" field. Fill the
`<…>` placeholders once your links + real benchmark are ready.*

---

## Solution name
**DockPulse — GPU-accelerated rebalancing early-warning for bike-share operations**

## One-line description
DockPulse tells a bike-share operations dispatcher which docking stations will run empty or
overflow in the next hour — as a ranked alert list, a live risk map, and an AI-written ops
briefing — powered by a GPU-accelerated pipeline over millions of BigQuery trip records.

## Problem
Bike-share dispatchers decide every hour where to send rebalancing crews. That decision
depends on aggregating tens of millions of trips into per-station, per-hour flow — too slow on
CPU to act on in time, so crews respond *after* stations are already empty and riders are
stranded.

## Solution
A pipeline ingests London bike-share trips from **BigQuery**, computes per-station net flow by
hour-of-week using **RAPIDS cuDF on an NVIDIA GPU**, and scores each station's empty/full
risk. A **Streamlit** dashboard shows a risk map + ranked "rebalance now" alerts, and
**Gemini** turns the top alerts into a plain-English shift briefing. The GPU work runs once
offline (and is benchmarked against CPU), so the app serves tiny precomputed artifacts and
deploys free.

## Acceleration impact (the before/after)
Running the identical `build_features()` on `<N_TRIPS>` trips: **pandas (CPU) `<CPU>`s vs cuDF
(GPU) `<GPU>`s → `<SPEEDUP>`× faster.** Time-to-insight drops from minutes to seconds, letting
the dispatcher act *before* a station fails rather than after.

## Tech stack
- **Google Cloud:** BigQuery (source data), Gemini (ops briefing)
- **NVIDIA:** RAPIDS cuDF (GPU feature engineering + CPU-vs-GPU benchmark)
- **App:** Streamlit + pydeck, deployed on Streamlit Community Cloud

## Links
- **Live prototype:** `<streamlit-app-url>`
- **GitHub (public):** `<github-repo-url>`
- **Demo video:** `<video-url>`
- **Pitch deck:** `<deck-url-or-attached>`

## Real user & recurring decision
Bike-share operations dispatcher — hourly decision on crew dispatch for rebalancing.
Secondary user: commuters checking dock availability.

## What's next
Live streaming feed, XGBoost forecast with weather signal, multi-city support, Cloud Run
deployment with hourly re-scoring.
