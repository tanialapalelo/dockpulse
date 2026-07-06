"""Generate a YouTube thumbnail (1280x720) for the DockPulse demo video.

YouTube best practice: big bold text, high contrast, readable at small size,
3-4 text elements max. Run: python docs/build_thumbnail.py
Output: docs/thumbnail.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
BENCH = json.loads((ROOT / "data" / "benchmark.json").read_text())
SPEEDUP = f"{BENCH['speedup']}×"

NVIDIA = "#76B900"
GOOGLE = "#4285F4"
INK = "#0B0D10"
WHITE = "#FFFFFF"
RED = "#E23B3B"
BLUE = "#3B82F6"
GREY = "#9CA3AF"

plt.rcParams["font.family"] = "DejaVu Sans"

# 1280x720 at 100 dpi = 12.8 x 7.2 inches
fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
ax.set_xlim(0, 12.8); ax.set_ylim(0, 7.2); ax.axis("off")
fig.patch.set_facecolor(INK)
ax.add_patch(plt.Rectangle((0, 0), 12.8, 7.2, color=INK, zorder=0))

# decorative faint map-dot cluster, right side (evokes the risk map)
rng = np.random.default_rng(3)
for _ in range(70):
    x = rng.uniform(7.6, 12.4)
    y = rng.uniform(0.5, 6.8)
    c = rng.choice([RED, BLUE, "#2E7D32"], p=[0.28, 0.22, 0.5])
    r = rng.uniform(0.05, 0.16)
    ax.add_patch(plt.Circle((x, y), r, color=c, alpha=0.85, zorder=1))

# left-side scrim so text stays readable over the dots
ax.add_patch(plt.Rectangle((0, 0), 8.3, 7.2, color=INK, alpha=0.97, zorder=2))

# top accent bar
ax.add_patch(plt.Rectangle((0, 6.95), 12.8, 0.25, color=NVIDIA, zorder=3))

# title
ax.text(0.55, 5.55, "DockPulse", fontsize=80, weight="bold", color=WHITE, zorder=4, va="center")
ax.text(0.6, 4.75, "Bike-share rebalancing, before it fails", fontsize=26,
        color=GREY, weight="bold", zorder=4, va="center")

# big speedup badge
ax.add_patch(FancyBboxPatch((0.55, 1.15), 4.55, 2.85, boxstyle="round,pad=0.03,rounding_size=0.12",
                              linewidth=0, facecolor="#12210A", zorder=4))
ax.text(2.8, 3.25, SPEEDUP, fontsize=95, weight="bold", color=NVIDIA, ha="center", va="center", zorder=5)
ax.text(2.8, 1.75, "FASTER ON GPU", fontsize=22, weight="bold", color=WHITE, ha="center", va="center", zorder=5)

# tech chips bottom-left
chip_y = 0.4
chip_x = 0.55
for label, color in [("BigQuery", GOOGLE), ("RAPIDS cuDF", NVIDIA), ("Gemini", GOOGLE)]:
    w = 0.22 + 0.155 * len(label)
    ax.add_patch(FancyBboxPatch((chip_x, chip_y), w, 0.5, boxstyle="round,pad=0.02,rounding_size=0.09",
                                  linewidth=0, facecolor=color, zorder=5))
    ax.text(chip_x + w / 2, chip_y + 0.25, label, fontsize=15, weight="bold",
            color=WHITE, ha="center", va="center", zorder=6)
    chip_x += w + 0.2

fig.savefig(ROOT / "docs" / "thumbnail.png", facecolor=INK, bbox_inches=None, pad_inches=0)
plt.close(fig)
print(f"Saved docs/thumbnail.png  (speedup badge: {SPEEDUP})")
