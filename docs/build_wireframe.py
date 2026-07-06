"""Generate a low-fidelity UI wireframe of the DockPulse screen layout.

This is intentionally NOT a screenshot — it's a plain, greyscale "design sketch"
showing the planned regions of the interface (sidebar, KPIs, map, briefing,
alerts, benchmark). It's the conceptual counterpart to the real, colourful
screenshots used in the "Snapshots of the prototype" slide.

Run:  python docs/build_wireframe.py
Output: docs/diagram_wireframe.png
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#111418"
GREY = "#6B7280"
LINE = "#9CA3AF"
PANEL = "#F3F4F6"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"


def region(ax, x, y, w, h, label, sub=None, fontsize=13):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.04",
        linewidth=1.4, edgecolor=LINE, facecolor=PANEL, linestyle="--", zorder=1,
    ))
    ty = y + h / 2 + (0.14 if sub else 0)
    ax.text(x + w / 2, ty, label, ha="center", va="center",
             fontsize=fontsize, color=INK, weight="bold", zorder=2)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.22, sub, ha="center", va="center",
                 fontsize=fontsize - 3.5, color=GREY, zorder=2, wrap=True)


fig, ax = plt.subplots(figsize=(13.3, 7.2), dpi=200)
ax.set_xlim(0, 13.3); ax.set_ylim(0, 7.2); ax.axis("off")

# outer "browser window" frame
ax.add_patch(FancyBboxPatch((0.15, 0.15), 13.0, 6.9, boxstyle="round,pad=0.02,rounding_size=0.05",
                              linewidth=2, edgecolor=INK, facecolor=WHITE, zorder=0))
# fake browser chrome dots
for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
    ax.add_patch(plt.Circle((0.55 + i * 0.28, 6.75), 0.08, color=c, zorder=3))
ax.text(6.65, 6.75, "dockpulse-app.streamlit.app", ha="center", va="center",
         fontsize=10, color=GREY, zorder=3)
ax.plot([0.15, 13.15], [6.55, 6.55], color=LINE, linewidth=1, zorder=1)

# sidebar (left strip)
region(ax, 0.35, 0.35, 2.5, 6.0, "SIDEBAR",
       "hour-of-week slider\nalerts-to-show slider\ndata-source note", fontsize=13)

# header / KPI strip
region(ax, 3.05, 5.55, 9.9, 0.8, "HEADER + KPI ROW",
       "title  ·  stations at risk  ·  emptying  ·  filling  ·  GPU speed-up", fontsize=13)

# risk map (left main)
region(ax, 3.05, 2.15, 5.9, 3.2, "RISK MAP",
       "stations colour-coded by risk\n(red = emptying, blue = filling, green = ok)", fontsize=14)

# gemini briefing (right main)
region(ax, 9.15, 2.15, 3.8, 3.2, "GEMINI OPS BRIEFING",
       "AI-written summary\nof top alerts", fontsize=13)

# ranked alerts table (bottom strip)
region(ax, 3.05, 1.05, 9.9, 0.9, "RANKED ALERTS TABLE",
       "station · status · risk · net flow · bikes to move · docks", fontsize=13)

# acceleration proof (bottom strip)
region(ax, 3.05, 0.35, 9.9, 0.55, "ACCELERATION PROOF — pandas (CPU) vs cuDF (GPU) bar chart",
       fontsize=12.5)

fig.tight_layout(pad=0.4)
fig.savefig("docs/diagram_wireframe.png", facecolor="white", bbox_inches="tight")
plt.close(fig)
print("Saved docs/diagram_wireframe.png")
