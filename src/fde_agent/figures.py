# matplotlib's type stubs leave **kwargs untyped, which strict pyright reports on
# every plotting call. Relax only that one rule, only in this file.
# pyright: reportUnknownMemberType=false
"""Exploration charts: which flags (alone, in pairs, in combinations) drive low reviews.

Run:  uv run python -m fde_agent.figures   → writes docs/figures/*.png
"""

import itertools
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to files; no display needed
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from fde_agent.processed import FLAGS, OUTCOME, order_table

FIG_DIR = Path(__file__).resolve().parents[2] / "docs" / "figures"
MIN_N = 100  # hide any cell/edge with fewer orders than this (too noisy)

# Reference palette (dataviz skill): light surface, text inks, one blue series,
# a blue sequential ramp for magnitude.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
NA_FILL = "#f0efec"
SEQ = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "text.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 10,
    }
)


def rate(t: pd.DataFrame, mask: "pd.Series[bool]") -> tuple[float, int]:
    """(P(low_review | mask), number of orders in mask)."""
    n = int(mask.sum())
    return (float(t.loc[mask, OUTCOME].mean()) if n else math.nan), n


def _save(fig: Figure, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _cell_text_color(value: float, vmax: float) -> str:
    return SURFACE if value / vmax > 0.55 else INK


def fig1_single_flags(t: pd.DataFrame) -> Path:
    base = float(t[OUTCOME].mean())
    rows = sorted(((f, *rate(t, t[f])) for f in FLAGS), key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(8, 4.6))
    names = [r[0] for r in rows]
    vals = [100 * r[1] for r in rows]
    ax.barh(names, vals, color=BLUE, height=0.6)
    ax.axvline(100 * base, color=INK_2, linestyle="--", linewidth=1)
    ax.text(
        100 * base + 0.8,
        len(rows) - 0.4,
        f"all orders {100 * base:.1f}%",
        color=INK_2,
        va="top",
        fontsize=9,
    )
    for i, (_, p, n) in enumerate(rows):
        ax.text(
            100 * p + 0.8,
            i,
            f"{100 * p:.1f}%  (n={n:,})",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of orders with a 1–2★ review")
    ax.set_title(
        "One flag at a time: which conditions go with bad reviews?",
        loc="left",
        fontsize=12,
    )
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    return _save(fig, "fig1_single_flags.png")


def pair_table(t: pd.DataFrame) -> pd.DataFrame:
    """Every pair (A, B): n and P(low) for A∧B, plus each flag alone."""
    recs: list[dict[str, object]] = []
    for a, b in itertools.combinations(FLAGS, 2):
        p_ab, n_ab = rate(t, t[a] & t[b])
        p_a, _ = rate(t, t[a])
        p_b, _ = rate(t, t[b])
        recs.append(
            {
                "a": a,
                "b": b,
                "n": n_ab,
                "p_ab": p_ab,
                "p_a": p_a,
                "p_b": p_b,
                "gain": p_ab - max(p_a, p_b),
            }
        )
    return pd.DataFrame(recs)


def fig2_pair_matrix(t: pd.DataFrame) -> Path:
    flags = list(FLAGS)
    k = len(flags)
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    vmax = 1.0
    for i, a in enumerate(flags):
        for j, b in enumerate(flags):
            mask = t[a] if i == j else t[a] & t[b]
            p, n = rate(t, mask)
            if n < MIN_N:
                ax.add_patch(Rectangle((j, i), 1, 1, color=NA_FILL, ec=SURFACE, lw=2))
                ax.text(
                    j + 0.5,
                    i + 0.5,
                    f"n<{MIN_N}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color=INK_2,
                )
                continue
            ax.add_patch(Rectangle((j, i), 1, 1, color=SEQ(p / vmax), ec=SURFACE, lw=2))
            ax.text(
                j + 0.5,
                i + 0.5,
                f"{100 * p:.0f}%",
                ha="center",
                va="center",
                fontsize=8,
                color=_cell_text_color(p, vmax),
                fontweight="bold" if i == j else "normal",
            )
    ax.set_xlim(0, k)
    ax.set_ylim(k, 0)
    ax.set_xticks([x + 0.5 for x in range(k)], flags, rotation=40, ha="right")
    ax.set_yticks([y + 0.5 for y in range(k)], flags)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    sm = plt.cm.ScalarMappable(cmap=SEQ, norm=Normalize(0, 100))
    fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02, label="% 1–2★ reviews")
    ax.set_title(
        "Two flags together (A AND B): % bad reviews\n"
        "diagonal (bold) = flag alone · all orders = "
        f"{100 * float(t[OUTCOME].mean()):.1f}%",
        loc="left",
        fontsize=12,
    )
    return _save(fig, "fig2_pair_matrix.png")


def _truth_table(ax: Axes, t: pd.DataFrame, a: str, b: str) -> None:
    for i, a_val in enumerate([True, False]):
        for j, b_val in enumerate([True, False]):
            mask = (t[a] == a_val) & (t[b] == b_val)
            p, n = rate(t, mask)
            ax.add_patch(Rectangle((j, i), 1, 1, color=SEQ(p), ec=SURFACE, lw=3))
            ax.text(
                j + 0.5,
                i + 0.42,
                f"{100 * p:.0f}%",
                ha="center",
                va="center",
                fontsize=14,
                color=_cell_text_color(p, 1.0),
                fontweight="bold",
            )
            ax.text(
                j + 0.5,
                i + 0.68,
                f"n={n:,}",
                ha="center",
                va="center",
                fontsize=8,
                color=_cell_text_color(p, 1.0),
            )
    ax.set_xlim(0, 2)
    ax.set_ylim(2, 0)
    ax.set_xticks([0.5, 1.5], [f"{b}", f"not {b}"])
    ax.set_yticks([0.5, 1.5], [f"{a}", f"not {a}"])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)


def fig3_truth_tables(t: pd.DataFrame) -> Path:
    pairs = pair_table(t)
    # exclude late+slow (slow mostly *is* late), rank by how much the pair beats
    # its stronger flag alone
    pairs = pairs[
        (pairs["n"] >= MIN_N) & ~((pairs["a"] == "late") & (pairs["b"] == "slow"))
    ]
    top = pairs.sort_values("gain", ascending=False).head(4)
    fig, axes = plt.subplots(2, 2, figsize=(9, 8))
    for ax, (_, r) in zip(axes.flat, top.iterrows(), strict=True):
        _truth_table(ax, t, str(r["a"]), str(r["b"]))
        ax.set_title(
            f"{r['a']} × {r['b']}  "
            f"(+{100 * float(r['gain']):.0f} pts vs stronger flag)",
            fontsize=10,
            loc="left",
        )
    fig.suptitle(
        "Truth tables: % bad reviews for each TRUE/FALSE combination",
        x=0.02,
        ha="left",
        fontsize=12,
    )
    fig.tight_layout()
    return _save(fig, "fig3_truth_tables.png")


SIGNAL_FLAGS = ["not_delivered", "late", "slow", "multi_item", "multi_seller"]


def fig4_intersections(t: pd.DataFrame) -> Path:
    """UpSet-style: exact combinations of the strongest flags (set intersections)."""
    # one tuple of True/False per order, e.g. (False, True, True, False, False)
    combo = pd.Series(
        list(zip(*(t[f].tolist() for f in SIGNAL_FLAGS), strict=True)), index=t.index
    )
    grouped = t.groupby(combo)[OUTCOME].agg(["size", "mean"])
    grouped = grouped[grouped["size"] >= 50].sort_values("mean", ascending=False)
    keys: list[tuple[bool, ...]] = list(grouped.index)
    fig, (top, mat) = plt.subplots(
        2, 1, figsize=(10, 6.4), sharex=True, gridspec_kw={"height_ratios": [3, 1.6]}
    )
    xs = range(len(keys))
    means = [100 * float(m) for m in grouped["mean"]]
    top.bar(xs, means, color=[SEQ(m / 100) for m in means], width=0.7)
    for x, m, n in zip(xs, means, grouped["size"], strict=True):
        top.text(
            x, m + 1.5, f"{m:.0f}%\nn={int(n):,}", ha="center", fontsize=7, color=INK
        )
    top.set_ylim(0, 110)
    top.set_ylabel("% 1–2★ reviews")
    top.grid(axis="y", color=GRID, linewidth=0.6)
    top.set_axisbelow(True)
    top.set_title(
        "Set intersections: each column is one exact combination of flags (●=TRUE)",
        loc="left",
        fontsize=12,
    )
    for x, key in enumerate(keys):
        on = [i for i, v in enumerate(key) if v]
        mat.scatter([x] * len(SIGNAL_FLAGS), range(len(SIGNAL_FLAGS)), s=40, color=GRID)
        if on:
            mat.scatter([x] * len(on), on, s=55, color=INK)
            mat.plot([x, x], [min(on), max(on)], color=INK, linewidth=2)
    mat.set_yticks(range(len(SIGNAL_FLAGS)), SIGNAL_FLAGS)
    mat.set_ylim(len(SIGNAL_FLAGS) - 0.5, -0.5)
    mat.set_xticks([])
    for s in mat.spines.values():
        s.set_visible(False)
    mat.tick_params(length=0)
    fig.tight_layout()
    return _save(fig, "fig4_intersections.png")


def fig5_flag_graph(t: pd.DataFrame) -> Path:
    """Graph: nodes = flags, edges = pairs whose AND beats the stronger flag alone."""
    base = float(t[OUTCOME].mean())
    flags = list(FLAGS)
    pos = {
        f: (
            math.cos(2 * math.pi * i / len(flags)),
            math.sin(2 * math.pi * i / len(flags)),
        )
        for i, f in enumerate(flags)
    }
    pairs = pair_table(t)
    edges = pairs[(pairs["n"] >= MIN_N) & (pairs["gain"] > 0.02)]
    fig, ax = plt.subplots(figsize=(8, 8))
    for _, r in edges.iterrows():
        (x1, y1), (x2, y2) = pos[str(r["a"])], pos[str(r["b"])]
        g = float(r["gain"])
        ax.plot(
            [x1, x2],
            [y1, y2],
            color=SEQ(min(1.0, 0.3 + 2 * g)),
            linewidth=1 + 25 * g,
            zorder=1,
            solid_capstyle="round",
        )
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            f"+{100 * g:.0f}",
            fontsize=8,
            color=INK_2,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.15", "fc": SURFACE, "ec": "none"},
        )
    for f, (x, y) in pos.items():
        p, n = rate(t, t[f])
        lift = p / base
        ax.scatter(
            [x],
            [y],
            s=300 + 900 * math.sqrt(n / len(t)),
            color=SEQ(min(1.0, p)),
            edgecolors=SURFACE,
            linewidths=2,
            zorder=2,
        )
        ax.text(
            x * 1.32,
            y * 1.32,
            f"{f}\n{100 * p:.0f}% · lift {lift:.1f}×",
            ha="center",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        "Flag graph: node = flag (size ∝ orders, shade = % bad reviews)\n"
        "edge = pair that is worse together than its stronger flag alone "
        "(+pts)",
        loc="left",
        fontsize=11,
    )
    return _save(fig, "fig5_flag_graph.png")


def fig6_days_late(t: pd.DataFrame) -> Path:
    d = t.dropna(subset=["days_late"])
    d = d[(d["days_late"] >= -30) & (d["days_late"] <= 30)]
    g = d.groupby(d["days_late"].astype(int))[OUTCOME].agg(["size", "mean"])
    g = g[g["size"] >= 30]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(g.index, 100 * g["mean"], color=BLUE, linewidth=2, marker="o", markersize=4)
    ax.axvline(0, color=INK_2, linestyle="--", linewidth=1)
    ax.text(0.5, 95, "← early   |   late →", color=INK_2, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_xlabel("days delivered after the estimated date (negative = early)")
    ax.set_ylabel("% 1–2★ reviews")
    ax.set_title(
        "Where does lateness start to hurt? (days with 30+ orders)",
        loc="left",
        fontsize=12,
    )
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    return _save(fig, "fig6_days_late.png")


ALL_FIGURES = (
    fig1_single_flags,
    fig2_pair_matrix,
    fig3_truth_tables,
    fig4_intersections,
    fig5_flag_graph,
    fig6_days_late,
)


if __name__ == "__main__":
    table = order_table()
    for make in ALL_FIGURES:
        print(f"wrote {make(table)}")
