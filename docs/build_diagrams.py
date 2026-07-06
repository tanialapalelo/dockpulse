"""Generate the two deck diagrams (process flow + architecture) as clean PNGs.

Run:  python docs/build_diagrams.py
Output: docs/diagram_flow.png, docs/diagram_architecture.png

Plain white background + the NVIDIA-green / Google-blue palette, matching the
official deck template style, so they drop straight into slides 6 & 7.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MplPath

NVIDIA = "#76B900"
GOOGLE = "#4285F4"
INK = "#111418"
GREY = "#5F6B7A"
LIGHT = "#F3F5F7"
WHITE = "#FFFFFF"

plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, x, y, w, h, text, face, edge=None, text_color=WHITE, fontsize=13, weight="bold"):
    edge = edge or face
    b = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=edge, facecolor=face, zorder=2,
    )
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, color=text_color, weight=weight, zorder=3, wrap=True)
    return b


def arrow(ax, p1, p2, color=INK, style="-|>", lw=2.2, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=18,
                          linewidth=lw, color=color, zorder=1,
                          connectionstyle=connectionstyle, shrinkA=2, shrinkB=2)
    ax.add_patch(a)


def label(ax, x, y, text, color=GREY, fontsize=11, weight="normal", ha="center"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=fontsize, color=color, weight=weight)


# =============================================================================
# Diagram 1 — Process flow / use-case (the dispatcher's journey)
# =============================================================================
fig, ax = plt.subplots(figsize=(13.3, 5.2), dpi=200)
ax.set_xlim(0, 13.3); ax.set_ylim(0, 5.2); ax.axis("off")

steps = [
    ("1\nOpen\nDockPulse", GREY),
    ("2\nSelect\nhour-of-week", GOOGLE),
    ("3\nSee risk map\n+ ranked alerts", NVIDIA),
    ("4\nRead Gemini\nbriefing", GOOGLE),
    ("5\nDispatch crew to\ntop-risk station", INK),
]
bw, bh, gap = 2.15, 1.7, 0.35
total_w = len(steps) * bw + (len(steps) - 1) * gap
x0 = (13.3 - total_w) / 2
y0 = 2.3

centers = []
for i, (text, color) in enumerate(steps):
    x = x0 + i * (bw + gap)
    box(ax, x, y0, bw, bh, text, color, fontsize=12.5)
    centers.append((x, x + bw))
    if i > 0:
        arrow(ax, (centers[i-1][1], y0 + bh / 2), (x, y0 + bh / 2))

# loop-back arrow: step 5 -> step 2, labelled "re-check in 30 min"
last_x = centers[-1][0] + bw / 2
second_x = centers[1][0] + bw / 2
arrow(ax, (last_x, y0 + bh + 0.05), (second_x, y0 + bh + 0.05),
      color=NVIDIA, connectionstyle="arc3,rad=-0.35")
label(ax, (last_x + second_x) / 2, y0 + bh + 1.05, "re-check in 30 minutes",
      color=NVIDIA, fontsize=11.5, weight="bold")

label(ax, 13.3 / 2, 0.55,
      "User: bike-share operations dispatcher  ·  Recurring decision: where to send rebalancing crews this hour",
      color=INK, fontsize=12, weight="bold")

fig.tight_layout(pad=0.6)
fig.savefig("docs/diagram_flow.png", facecolor="white", bbox_inches="tight")
plt.close(fig)
print("Saved docs/diagram_flow.png")


# =============================================================================
# Diagram 2 — Architecture (Google Cloud data + NVIDIA acceleration + app/decision)
# =============================================================================
fig, ax = plt.subplots(figsize=(13.3, 6.0), dpi=200)
ax.set_xlim(0, 13.3); ax.set_ylim(0, 6.0); ax.axis("off")

# layer band backgrounds
def band(x, w, ytext, text, color):
    ax.add_patch(FancyBboxPatch((x, 0.15), w, 5.15, boxstyle="round,pad=0.02,rounding_size=0.06",
                                  linewidth=1.4, edgecolor=color, facecolor="none", linestyle="--", zorder=0))
    ax.text(x + w / 2, ytext, text, ha="center", va="center", fontsize=11.5, color=color, weight="bold")

band(0.25, 4.2, 5.65, "GOOGLE CLOUD — DATA LAYER", GOOGLE)
band(4.65, 4.2, 5.65, "NVIDIA — ACCELERATION LAYER (offline / batch)", NVIDIA)
band(9.05, 4.05, 5.65, "APPLICATION / DECISION LAYER", INK)

# boxes
box(ax, 0.55, 3.7, 3.6, 1.3, "BigQuery\nlondon_bicycles\n(3.2M+ real trips)", GOOGLE, fontsize=12)
box(ax, 0.55, 1.6, 3.6, 1.3, "extract_bq.py\nbounded date window", GREY, fontsize=12)
arrow(ax, (2.35, 3.7), (2.35, 2.9))

box(ax, 4.95, 3.7, 3.6, 1.3, "Colab T4 GPU\nbuild_features()", NVIDIA, fontsize=12)
box(ax, 4.95, 1.6, 3.6, 1.3, "pandas (CPU) vs\ncuDF (GPU) — timed", NVIDIA, edge="#4d7a00", fontsize=12)
arrow(ax, (4.15, 2.25), (4.95, 4.1))
arrow(ax, (6.75, 3.7), (6.75, 2.9))

box(ax, 9.35, 3.9, 3.55, 1.1, "station_features.parquet\n+ benchmark.json", LIGHT, edge=GREY, text_color=INK, fontsize=11.5)
arrow(ax, (8.55, 4.35), (9.35, 4.45))

box(ax, 9.35, 2.2, 3.55, 1.3, "Streamlit app\nrisk map + alerts", INK, fontsize=12)
arrow(ax, (11.1, 3.9), (11.1, 3.5))

box(ax, 9.35, 0.4, 3.55, 1.3, "Gemini\nops briefing", GOOGLE, fontsize=12)
arrow(ax, (11.1, 2.2), (11.1, 1.7))

fig.tight_layout(pad=0.6)
fig.savefig("docs/diagram_architecture.png", facecolor="white", bbox_inches="tight")
plt.close(fig)
print("Saved docs/diagram_architecture.png")
