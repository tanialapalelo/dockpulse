# DockPulse — 3-Minute Demo Video Script

Follows NVIDIA's **4-beat storyboard**: ① User + Data → ② Build Pipeline → ③ Add
Acceleration → ④ Show Decision. Record with QuickTime / Loom / OBS screen capture. Speak
over a live screen recording of the app + a quick flash of the Colab benchmark.

**Total ≈ 3:00. Practice once, record once, don't over-polish.**

---

### 0:00–0:25 · Hook + the real user  *(beat ①)*
> "This is a bike-share dock that's completely empty — and a commuter who's now late for
> work. Multiply that by a whole city, every rush hour. The person who has to prevent it is
> the **operations dispatcher**, and every hour they make the same call: *where do I send
> crews before stations run empty?* I built **DockPulse** to answer that in seconds."

*(On screen: the app's title + risk map already loaded.)*

### 0:25–1:00 · The data + the pipeline  *(beat ②)*
> "DockPulse starts from **BigQuery's London bike-share dataset — millions of real trips**.
> A pipeline cleans them and computes, for every station and every hour of the week, how many
> bikes leave versus arrive — the **net flow**. That's what predicts an empty or overflowing
> dock."

*(On screen: scrub the **hour-of-week slider** from morning to evening rush — watch the map
recolour. Hover a red dot to show the tooltip.)*

### 1:00–1:40 · Acceleration  *(beat ③ — the money moment)*
> "Aggregating tens of millions of trips on a CPU is slow — too slow to act on. So the heavy
> feature engineering runs on an **NVIDIA GPU with RAPIDS cuDF**. Same code, different engine:
> pandas took **[CPU]s**, cuDF took **[GPU]s** — that's **[N]× faster**. Minutes of
> waiting become seconds, so the dispatcher gets the answer while it's still useful."

*(On screen: cut to the Colab benchmark output / the app's "Acceleration proof" bar chart.
Say the speedup number clearly.)*

### 1:40–2:30 · The decision  *(beat ④)*
> "Here's what the dispatcher actually sees: a **ranked 'rebalance now' list**. Top of the
> list — **[station name]** — high risk, ~[N] bikes leaving this hour: send a resupply crew.
> And **Gemini** writes the whole shift briefing in plain English, so a new dispatcher knows
> exactly what to do in twenty seconds."

*(On screen: point at the top alert row, then the Gemini briefing panel.)*

### 2:30–3:00 · Impact + close
> "Fewer empty docks, fewer stranded riders, crews dispatched **before** failure instead of
> after. It runs on **BigQuery, RAPIDS, and Gemini**, deploys free, and it's live at this
> link. Built in 24 hours. Thanks for watching."

*(On screen: end card with the live app URL + GitHub URL.)*

---

### Recording checklist
- [ ] App running with **real** Colab data (or clearly-labelled synthetic if GPU run pending)
- [ ] Gemini key set so the briefing shows "✅ Gemini"
- [ ] Say the **speedup number** out loud (judges listen for it)
- [ ] Keep it under 3:00 — leave the empty-dock hook in, cut anything else if over
- [ ] Export 1080p, upload unlisted to YouTube / Drive, set link to "anyone with link"
