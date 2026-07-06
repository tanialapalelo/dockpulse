# 🚲 DockPulse — will your docks run empty next hour?

**A GPU-accelerated rebalancing early-warning board for bike-share operations.**

Built for the **Hack2Skill × Google Cloud × NVIDIA — GenAI Academy APAC Edition** (PS2:
*a data intelligence tool people would actually use, where acceleration makes a decision
faster/better*).

![status](https://img.shields.io/badge/status-prototype-76b900)

---

## The one-minute pitch

A bike-share **operations dispatcher** makes the same decision every hour: *which docking
stations are about to run empty or overflow, so I know where to send rebalancing crews?*
Today that decision is reactive — crews arrive **after** a station is already empty and riders
are stranded.

DockPulse turns tens of millions of historical trips into a **live risk map + ranked
"rebalance now" alerts + a plain-English ops briefing**, and it does the heavy lifting on a
**GPU** so the insight is ready in seconds instead of minutes.

| Who | Decision | Help |
|---|---|---|
| Bike-share dispatcher (& commuters) | Where to move bikes in the next hour | Ranked alerts + map + AI briefing |

## What it does

- **Risk map** — every station coloured by empty/full risk for a selected hour-of-week.
- **Ranked alerts** — the top stations to act on, with the concrete action ("move ~N bikes").
- **AI ops briefing** — Gemini summarises the top alerts into a 20-second read.
- **Acceleration proof** — side-by-side pandas (CPU) vs cuDF (GPU) timing on the same pipeline.

## Architecture

```
BigQuery (london_bicycles)                ← Google Cloud data layer
   │  Colab T4 notebook
   ▼
build_features()  ──timed on── pandas (CPU)  vs  cuDF (GPU)   ← NVIDIA acceleration layer
   ▼
station_features.parquet + benchmark.json  (tiny artifacts)
   ▼
Streamlit app ──selected hour──▶ risk score ──▶ map + alerts   ← application / decision layer
   │
   └──top alerts──▶ Gemini ──▶ ops briefing                    ← Google Cloud (Gemini)
```

**Why the split?** The GPU work runs once, offline, in Colab (reproducible + benchmarked);
the app serves tiny precomputed files, so it deploys free and never needs a GPU at runtime.

### Tech used (meets the "2+ Google Cloud + NVIDIA" rule)
- **Google Cloud:** BigQuery (source data) · Gemini (ops briefing)
- **NVIDIA:** RAPIDS **cuDF** (feature engineering + benchmark)
- **App:** Streamlit + pydeck, deployed on Streamlit Community Cloud

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.make_sample_data      # creates synthetic data so it runs with zero setup
streamlit run app.py
```

Add a Gemini key for the AI briefing (optional — there's a template fallback):

```bash
export GEMINI_API_KEY="your-google-ai-studio-key"
```

## Produce the real (GPU) numbers

1. Open `notebooks/dockpulse_gpu_pipeline.ipynb` in **Google Colab**.
2. `Runtime > Change runtime type > T4 GPU`.
3. Set `PROJECT_ID` to your GCP project, run all cells.
4. Download `station_features.parquet` + `benchmark.json` into `data/`, commit, push.
   Streamlit Cloud redeploys automatically with live numbers.

## Deploy (free public URL)

1. Push this repo to GitHub (public).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → pick this repo →
   main file `app.py`.
3. Add `GEMINI_API_KEY` under **App → Settings → Secrets**.
4. Deploy → you get a public `*.streamlit.app` URL.

## Tests

```bash
python -m pytest -q          # feature-engineering + risk-scoring unit tests
```

## Project layout

```
app.py                     Streamlit serving layer
src/features.py            build_features() — same code on pandas & cuDF (the honest benchmark)
src/score_risk.py          explainable empty/full risk score + action
src/gemini_brief.py        Gemini briefing with template fallback
src/extract_bq.py          BigQuery extract query
src/make_sample_data.py    synthetic data (demo safety net)
notebooks/…gpu_pipeline    Colab: BigQuery → cuDF → benchmark → artifacts
data/                      generated artifacts
docs/                      design spec, deck outline, demo script, submission brief
tests/                     unit tests
```

## License
MIT — see `LICENSE`.
