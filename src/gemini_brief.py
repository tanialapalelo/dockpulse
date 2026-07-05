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


def brief(alerts: pd.DataFrame, hour_label: str) -> tuple[str, str]:
    """Return (briefing_markdown, source) where source is 'gemini' or 'template'."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _template_brief(alerts, hour_label), "template"

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"))

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
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        if not text:
            raise ValueError("empty response")
        return text, "gemini"
    except Exception:
        # any failure -> graceful fallback, demo never breaks
        return _template_brief(alerts, hour_label), "template"
