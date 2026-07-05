# DockPulse — Design Spec

**Date:** 2026-07-05
**Author:** tania
**Event:** Hack2Skill × Google Cloud × NVIDIA — GenAI Academy APAC Edition
**Track:** PS2 — "Create a data intelligence tool people would actually use, and show how acceleration helps them make a faster or better decision."

---

## 1. One-liner

DockPulse is a rebalancing early-warning dashboard that tells a bike-share operations
dispatcher **which docking stations will run empty or full in the next hour**, ranked by
risk, on a live map — powered by a **GPU-accelerated (RAPIDS/cuDF)** pipeline over tens of
millions of historical trips from **BigQuery**, with a plain-English ops briefing written by
**Gemini**.

## 2. The five rubric questions (NVIDIA "Strong Submission Checklist")

| Requirement | DockPulse answer |
|---|---|
| **Real user** | Bike-share **operations dispatcher**; recurring decision made *every hour*: where to send rebalancing crews. Secondary user: a commuter deciding if a bike/dock will be free. |
| **Decision bottleneck** | Today rebalancing is reactive/manual. Tens of millions of trip rows must be aggregated into per-station hourly flow; doing this on CPU is slow, so crews react *after* stations go empty. |
| **Data pipeline** | BigQuery ingest → clean → cuDF feature engineering (per-station, per-hour-of-week net flow + trend + volatility) → risk scoring → map + ranked alerts. |
| **Useful output** | Ranked "rebalance now" alert list + risk map + per-station action ("move ~N bikes") + Gemini ops briefing. |
| **Acceleration proof** | Same feature-engineering function timed on **pandas (CPU) vs cuDF (GPU T4)** over the full trip table; report speedup, rows/sec, and time-to-insight. |

## 3. Scope (YAGNI)

**In scope**
- One city: London (`bigquery-public-data.london_bicycles`) — largest free dataset → best GPU story.
- Statistical risk model (historical net-flow by hour-of-week + recent-trend adjustment). Explainable, fast, defensible.
- Streamlit app with: KPI header, risk map, ranked alerts, benchmark panel, Gemini briefing, hour-of-week selector.
- Colab T4 notebook that produces the real artifacts + the benchmark.
- Synthetic-data generator so the app runs/deploys with zero external dependencies (demo safety net).

**Explicitly out of scope (v1)**
- Live/streaming data, multiple cities, user auth, real-time GPU inference in the web app,
  heavy ML (XGBoost only as a stretch goal if time remains), Cloud Run (stretch).

## 4. Architecture — two clean layers

### Layer A — Engine room (Colab T4 notebook) — *the acceleration proof*
1. Query trips from BigQuery → `raw_trips.parquet` (bounded slice to stay in free tier).
2. Run `build_features(df)` on **pandas** → record `cpu_time`.
3. Run the **same** `build_features(df)` on a **cuDF** DataFrame → record `gpu_time`.
4. Score risk → export artifacts: `station_features.parquet`, `benchmark.json`.
5. Commit artifacts to the repo (or upload to Cloud Storage as stretch).

### Layer B — Serving layer (Streamlit, deployed) — *the working prototype*
- Loads the tiny precomputed artifacts (no GPU needed at serve time).
- Computes the risk score for the **selected hour-of-week** on the fly (≈800 stations — trivial).
- Renders map + alerts + benchmark + Gemini briefing.
- If real artifacts are absent, falls back to the **synthetic generator** so it always runs.

> **Why split?** Running a GPU inside a live web app in 24h is a quota/cost/cold-start trap.
> Splitting keeps the GPU win reproducible + screenshottable, and lets the app deploy free
> and instantly. It is also honest architecture: batch precompute + lightweight serving.

## 5. Data flow

```
BigQuery london_bicycles.cycle_hire + cycle_stations
        │  (Colab notebook)
        ▼
  raw_trips (parquet)
        │  build_features()  ← timed on pandas AND cuDF
        ▼
  station_features.parquet   +   benchmark.json
        │  (committed to repo / GCS)
        ▼
  Streamlit app  ──selected hour──▶ score_risk()  ──▶ map + ranked alerts
        │
        └──top alerts──▶ Gemini ──▶ ops briefing (fallback: template)
```

## 6. Components (isolated, testable units)

| Unit | File | Responsibility | Depends on |
|---|---|---|---|
| Config | `src/config.py` | Constants: BQ table ids, thresholds, paths, demo hour | — |
| Extract | `src/extract_bq.py` | Query BigQuery → raw_trips parquet | google-cloud-bigquery |
| Features | `src/features.py` | **Library-agnostic** `build_features(df)` (works on pandas or cuDF): explode trips into departure/arrival events, aggregate net flow per station × hour-of-week, volatility | pandas API subset |
| Risk | `src/score_risk.py` | `score(features, hour_of_week)` → risk 0–100, status (empty/full/ok), suggested bikes to move | numpy |
| Briefing | `src/gemini_brief.py` | `brief(top_alerts)` via Gemini; **template fallback** if no key/error | google-generativeai |
| Sample data | `src/make_sample_data.py` | Generate realistic synthetic `station_features.parquet` + `benchmark.json` | numpy/pandas |
| App | `app.py` | Streamlit UI wiring all of the above | streamlit, pydeck |
| Notebook | `notebooks/dockpulse_gpu_pipeline.ipynb` | BQ → cuDF features → benchmark → artifacts | cudf, bigquery |

### Key artifacts (schemas)
- `station_features.parquet`: `station_id, station_name, lat, lon, docks_count, hour_of_week (0–167), mean_departures, mean_arrivals, net_flow, volatility`
- `benchmark.json`: `{ n_trips, cpu_seconds, gpu_seconds, speedup, rows_per_sec_cpu, rows_per_sec_gpu, gpu_name, generated_at }`

## 7. Risk model (explainable)

For a selected `hour_of_week`:
- `predicted_net_flow = mean_net_flow[station, hour_of_week]` (departures − arrivals).
- Net **outflow** (people take bikes) → **empty** risk. Net **inflow** → **full** risk.
- `pressure = predicted_net_flow / max(docks_count, 1)` over a 1-hour horizon.
- `risk = clip(100 * |pressure| / PRESSURE_FULL_SCALE, 0, 100)`, boosted by volatility.
- `status`: `EMPTY_RISK` if outflow-dominant & risk ≥ threshold; `FULL_RISK` if inflow-dominant & risk ≥ threshold; else `OK`.
- `bikes_to_move ≈ round(predicted_net_flow)` — the concrete action.

Stretch: replace the mean with an XGBoost regressor on (hour_of_week, recent trend, weather) — only if time remains. v1 ships the statistical model.

## 8. Deployment

- **Primary:** Streamlit Community Cloud — connect GitHub repo → instant public URL = the
  "working prototype link". `GEMINI_API_KEY` stored in Streamlit secrets.
- **Stretch:** containerize → Cloud Run (adds a GCP deploy story) if time remains.

## 9. Error handling / demo safety

- Missing real artifacts → auto-generate synthetic data (app never blank).
- Missing/failed Gemini → deterministic template briefing.
- BigQuery free-tier cap → notebook bounds the query (date range / LIMIT) and prints bytes billed.
- Map tiles fail → alerts table + benchmark still render.

## 10. Testing

- `build_features` unit test: tiny hand-made trip frame → known net-flow output; assert pandas
  and cuDF paths produce identical results.
- `score_risk` unit test: crafted feature row → expected status/risk band.
- App smoke test: launches, loads artifacts, renders without exception on synthetic data.
- Benchmark sanity: gpu_seconds < cpu_seconds; speedup printed.

## 11. Deliverables → rubric mapping

| Deliverable | Serves rubric criterion |
|---|---|
| Working Streamlit app (deployed) | Solution quality/functionality; Demo/UX |
| GitHub repo (code + notebook + artifacts) | Architecture/technical execution; Feasibility |
| Colab benchmark (CPU vs GPU) | Technical choices; Acceleration proof |
| PPT deck (10 slides, rubric-mapped) | Presentation |
| 3-min demo video (4-beat storyboard) | Demo/UX/presentation |
| Written brief (SUBMISSION.md) | Impact & use-case relevance |

## 12. 24-hour timeline

| Hrs | Phase |
|---|---|
| 0–2 | Repo + BigQuery access + Colab RAPIDS env + extract data |
| 2–6 | cuDF features + benchmark + risk scoring → export artifacts |
| 6–12 | Streamlit app (map, alerts, benchmark, briefing) |
| 12–15 | Deploy to Streamlit Cloud + polish |
| 15–19 | PPT deck + written brief |
| 19–22 | Record 3-min demo video |
| 22–24 | Buffer + README + submit |
