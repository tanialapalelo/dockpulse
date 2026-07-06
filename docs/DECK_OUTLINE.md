# DockPulse — Pitch Deck (10 slides)

Copy each slide's content into the required **"Prototype Submission Deck – Gen AI Academy
APAC Edition"** template. Every slide is mapped to a scoring criterion (each worth 20%).
Keep it visual: screenshots > paragraphs. Speaker notes are what you *say*, not what's on the slide.

Design tip: use the NVIDIA-green (#76B900) + Google-blue accents so it visually signals the
sponsor stack. One idea per slide, ≤ 20 words of on-slide text where possible.

---

## Slide 1 — Title
**DockPulse — will your docks run empty next hour?**
Subtitle: *GPU-accelerated rebalancing early-warning for bike-share operations.*
Your name · Gen AI Academy APAC · BigQuery · RAPIDS cuDF · Gemini
> *Speaker note:* "Every bike-share dispatcher fights the same hourly battle — I built an early-warning board for it."

## Slide 2 — The real user & the stuck decision  ·  *[Impact & relevance]*
- **Who:** a bike-share operations dispatcher (and every commuter who's found an empty dock).
- **Decision, every hour:** where do I send crews before stations run empty or overflow?
- **Today:** reactive. Crews arrive *after* riders are already stranded.
> *Speaker note:* Name the person. Judges reward a specific, real user with a recurring decision.

## Slide 3 — Why it's hard (the data bottleneck)  ·  *[Impact & relevance]*
- Tens of millions of trips → must become per-station, per-hour flow.
- On CPU this aggregation is slow, so insight arrives too late to act.
- "Stale forecast = empty dock = lost rider."
> *Speaker note:* This sets up *why acceleration matters* — the bottleneck is data volume vs. time-to-decision.

## Slide 4 — The solution (product shot)  ·  *[Solution quality]*
- Full-bleed screenshot of the app: risk map + ranked alerts + KPI header.
- Callouts: 🔴 emptying · 🔵 filling · ranked "rebalance now" list · one-click hour selector.
> *Speaker note:* Show, don't tell. Point at the top alert and read the action out loud.

## Slide 5 — Architecture  ·  *[Architecture & technical execution]*
- The diagram from the README: BigQuery → Colab cuDF (CPU vs GPU) → artifacts → Streamlit → Gemini.
- Label the three layers: **Google Cloud data · NVIDIA acceleration · application/decision**.
> *Speaker note:* "Heavy GPU work runs once offline and is benchmarked; the app serves tiny files, so it's free and always up."

## Slide 6 — The data pipeline  ·  *[Architecture & technical execution]*
Four steps with icons: **Ingest+Clean → Analyze+Model → Score → Visualize+Act.**
- Ingest: BigQuery `london_bicycles`, ~N trips.
- Model: net-flow per station × hour-of-week + volatility.
- Act: risk score → ranked alerts → Gemini briefing.
> *Speaker note:* Mirrors NVIDIA's "Required Data Pipeline" slide — trace it end to end.

## Slide 7 — ⚡ Acceleration proof  ·  *[Technical choices & feasibility]* ← the money slide
- Big bar chart: **pandas (CPU) Xs  vs  cuDF (GPU) Ys → N× faster.**
- Same `build_features()` code, only the engine changes (fill in real Colab numbers).
- "Time-to-insight: minutes → seconds. Same laptop-free stack: Google Cloud + NVIDIA."
> *Speaker note:* This is the slide the NVIDIA judge is waiting for. Say the speedup number twice.

## Slide 8 — Gemini in the loop  ·  *[Solution quality]*
- Screenshot of the AI ops briefing.
- "Gemini turns the top alerts into a 20-second decision brief — with a template fallback so the demo never breaks."
> *Speaker note:* Shows GenAI is doing real work (decision support), not bolted on.

## Slide 9 — Impact & what's next  ·  *[Impact & relevance]*
- Impact: fewer empty docks, shorter rider wait, crews dispatched *before* failure.
- Scales to any city with an open trip feed; freshness improves with GPU (re-score hourly).
- Next: live feed, XGBoost forecast, Cloud Run deploy, weather signal.
> *Speaker note:* Connect back to "AI for better living / smarter communities."

## Slide 10 — Try it / links  ·  *[Demo & presentation]*
- **Live app:** `<streamlit URL>`  ·  **GitHub:** `<repo URL>`  ·  **Demo video:** `<link>`
- Stack badges: BigQuery · RAPIDS cuDF · Gemini · Streamlit.
- "Built in 24 hours."
> *Speaker note:* End on the working link. Invite them to click a station.

---

### Fill-in checklist before exporting
- [ ] Slide 7: real `cpu_seconds`, `gpu_seconds`, `speedup`, `n_trips` from `data/benchmark.json`
- [ ] Slides 4 & 8: real app screenshots (run locally or from the deployed URL)
- [ ] Slide 6: real trip count on the Ingest step
- [ ] Slide 10: live app URL, GitHub URL, demo video URL
