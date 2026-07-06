# DockPulse — Final Runbook & Submission Checklist

Everything that can be automated is done. This is the ordered list of the **human-only**
steps left to cross the finish line. Estimated time: ~2–3 focused hours + video.

Repo: https://github.com/tanialapalelo/dockpulse

---

## ✅ Already done (by the build)
- [x] Working Streamlit app (runs on synthetic data with zero setup)
- [x] Full pipeline: BigQuery extract → cuDF features → risk score → Gemini briefing
- [x] Unit tests passing (`python -m pytest -q`)
- [x] Public GitHub repo pushed
- [x] Colab GPU benchmark notebook
- [x] README, pitch-deck outline, demo script, submission brief, design spec

---

## 🧑‍💻 Step 1 — Deploy the live app (~10 min)  → gives you the *working prototype link*
1. Go to **https://share.streamlit.io** → sign in with GitHub.
2. **New app** → repo `tanialapalelo/dockpulse` → branch `main` → main file `app.py` → **Deploy**.
3. Once live, open **Manage app → Settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-google-ai-studio-key"
   GEMINI_MODEL = "gemini-1.5-flash"
   ```
4. Copy the public `https://<something>.streamlit.app` URL. ✅ *prototype link done.*

> It works immediately on the committed synthetic data. Swapping in real GPU numbers (Step 2)
> is what makes the acceleration slide truthful — do it if you possibly can.

## ⚡ Step 2 — Generate the REAL GPU benchmark (~30–40 min)  → makes the acceleration proof real
1. Open `notebooks/dockpulse_gpu_pipeline.ipynb` in **Google Colab**
   (Colab → File → Open notebook → GitHub → paste the repo URL).
2. **Runtime → Change runtime type → T4 GPU**.
3. In cell 2, set `PROJECT_ID = "<your-gcp-project>"`. Run all cells; approve the Google auth popup.
4. It prints the speedup and downloads `station_features.parquet` + `benchmark.json`.
5. Replace the files in your local `data/` with the downloaded ones, then:
   ```bash
   cd ~/projects/dockpulse
   git add data/station_features.parquet data/benchmark.json
   git commit -m "Add real GPU benchmark + London station features"
   git push
   ```
   Streamlit Cloud auto-redeploys with live numbers.

> If Colab/BigQuery fights you and time is short: the app still demos fine on synthetic data —
> just say "representative data" in the video and prioritise a clean, deployed demo.

## 🎞️ Step 3 — Record the demo video (~30 min)  → *demo video link*
1. Open `docs/DEMO_SCRIPT.md` — it's a word-for-word 3-minute script on the 4-beat storyboard.
2. Screen-record the deployed app (QuickTime/Loom/OBS). Scrub the hour slider, hover a red dot,
   show the alerts + Gemini briefing + acceleration bar chart. Say the **speedup number** aloud.
3. Upload unlisted to YouTube/Drive; set sharing to "anyone with link". Copy the URL.

## 📊 Step 4 — Build the deck (~45 min)  → *PPT link*
1. Open `docs/DECK_OUTLINE.md` — 10 slides, each mapped to a 20% scoring criterion.
2. Paste content into the official *"Prototype Submission Deck – Gen AI Academy APAC"* template.
3. Drop in: 2 app screenshots + the benchmark bar chart + the architecture diagram.
4. Fill Slide 7 with the real numbers from `data/benchmark.json`.

## 📝 Step 5 — Submit (~15 min)
Open `docs/SUBMISSION.md`, fill the `<…>` links, and paste into the Hack2Skill form:
- [ ] PPT (Step 4)
- [ ] Working prototype link (Step 1)
- [ ] GitHub public repo: `https://github.com/tanialapalelo/dockpulse`
- [ ] Demo video link (Step 3)
- [ ] Brief description (from `docs/SUBMISSION.md`)

---

## Priority order if you run out of time
1. **Deploy the app** (Step 1) — a working link beats everything.
2. **Record the video** (Step 3) — 20% of the score, and it carries the story.
3. **Deck** (Step 4) — 20% of the score.
4. **Real GPU numbers** (Step 2) — biggest credibility boost, but synthetic still tells the story.

A deployed app + a clear 3-minute video + a 10-slide deck = a complete, defensible submission —
even before the real GPU run. That's your CV-worthy finish. 🚀
