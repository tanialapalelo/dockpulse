"""Natural-language ops briefing via Gemini, with a deterministic fallback.

The fallback matters: if the API key is missing or the call fails during the live
demo, the app still produces a sensible briefing instead of crashing.
"""
from __future__ import annotations

import os

import pandas as pd

from . import config


def _template_brief(alerts: pd.DataFrame, hour_label: str) -> str:
    if alerts.empty:
        return f"**{hour_label}** — network balanced. No stations breach the risk threshold; no crews need dispatching this hour."

    empties = alerts[alerts["status"] == "EMPTY_RISK"]
    fulls = alerts[alerts["status"] == "FULL_RISK"]
    lines = [f"**{hour_label} — {len(alerts)} station(s) need attention.**", ""]
    if not empties.empty:
        top = empties.iloc[0]
        lines.append(
            f"- 🔴 **Emptying:** {len(empties)} stations trending empty. Priority: "
            f"**{top['station_name']}** (risk {top['risk']:.0f}, ~{abs(int(top['bikes_to_move']))} bikes leaving). "
            f"Send a resupply crew before the hour peaks."
        )
    if not fulls.empty:
        top = fulls.iloc[0]
        lines.append(
            f"- 🔵 **Filling:** {len(fulls)} stations trending full. Priority: "
            f"**{top['station_name']}** (risk {top['risk']:.0f}, ~{abs(int(top['bikes_to_move']))} bikes arriving). "
            f"Free up docks so returning riders aren't stranded."
        )
    lines.append("")
    lines.append("_Act on the top 3 now; re-check in 30 minutes._")
    return "\n".join(lines)


# Cached once a working model name is found, so we don't re-discover on every call.
_WORKING_MODEL: str | None = None

# Tried in order before falling back to asking the API what it currently supports.
# Model names get retired over time (e.g. gemini-1.5-flash) — rather than trust one
# hardcoded string forever, we try a short list of likely-current names first.
_CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-pro-latest",
]


def brief(alerts: pd.DataFrame, hour_label: str) -> tuple[str, str]:
    """Return (briefing_markdown, source) where source is 'gemini' or 'template'."""
    global _WORKING_MODEL
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _template_brief(alerts, hour_label), "template"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"[gemini_brief] configure failed: {e}")
        return _template_brief(alerts, hour_label), "template"

    rows = alerts[["station_name", "status", "risk", "bikes_to_move"]].to_dict("records")
    prompt = (
        "You are DockPulse, an operations copilot for a city bike-share dispatcher. "
        f"It is {hour_label}. Below are the stations at risk this hour (status EMPTY_RISK "
        "means bikes are leaving faster than they arrive; FULL_RISK means docks are filling). "
        "Write a concise, confident ops briefing (max 120 words) that: names the 2-3 most urgent "
        "stations, says whether to send bikes IN or free docks, and gives one clear next action. "
        "Use short markdown bullets. Do not invent stations.\n\n"
        f"At-risk stations: {rows}"
    )

    env_model = os.environ.get("GEMINI_MODEL", "").strip()
    tried: set[str] = set()
    candidates = [n for n in ([_WORKING_MODEL, env_model] + _CANDIDATE_MODELS) if n]
    last_err: Exception | None = None

    def _try(name: str) -> tuple[str, str] | None:
        nonlocal last_err
        if not name or name in tried:
            return None
        tried.add(name)
        try:
            model = genai.GenerativeModel(name)
            resp = model.generate_content(prompt)
            text = (resp.text or "").strip()
            if text:
                _WORKING_MODEL = name
                return text, "gemini"
        except Exception as e:
            last_err = e
        return None

    for name in candidates:
        result = _try(name)
        if result:
            return result

    # Last resort: ask the API which models it currently supports, rather than
    # guessing further hardcoded names.
    try:
        for m in genai.list_models():
            name = getattr(m, "name", "").split("/")[-1]
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" not in methods:
                continue
            result = _try(name)
            if result:
                return result
    except Exception as e:
        last_err = e

    # Any failure -> graceful fallback, demo never breaks. Logged (not shown in
    # the UI) so it's visible in Streamlit Cloud's app logs for debugging.
    print(f"[gemini_brief] all Gemini attempts failed, using template. Last error: {last_err}")
    return _template_brief(alerts, hour_label), "template"
