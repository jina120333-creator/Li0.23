#!/usr/bin/env python3
"""Extract the scour-depth time series from the 'bedLevels' functionObject
and compare it with Li, Yang & Yang (2020), Water 12, 2370, Figure 5.

The functionObject samples vertical alpha.a profiles 2.5 mm off the pier
surface (front, sideL, sideR). The bed elevation is the highest z at which
alpha.a crosses ALPHA_C (default 0.5), and the scour depth is measured
relative to the bed elevation at the reference time --t0. With the rigid-bed
precursor workflow the flow is already developed at t = 0 and the bed is
mobile from the start, so t0 = 0 (the default):

    t_exp = t_sim - t0,      S(t) = z_bed(t0) - z_bed(t)

Usage:
    python3 scripts/extract_scour.py [--t0 0] [--alpha-c 0.5] [--case DIR]

Writes scour_timeseries.csv and (if matplotlib is available) scour_vs_paper.png.
"""

import argparse
import csv
import glob
import math
import os
import sys

D = 0.04                      # pier diameter [m]
TSTAR_PER_SEC = math.sqrt(9.81 * 1.65 * (0.6e-3) ** 3) / D ** 2   # = 0.03696

# ---------------------------------------------------------------------------
# Reference data digitized from Fig. 5 of the paper (pixel analysis of the
# published PDF; axis calibration verified against t* = 133/266/931 to < 1
# t* unit). S/D reading uncertainty ~ +/- 0.02. The two early 'front' points
# marked ~ came from partially overlapping markers and are approximate.
# ---------------------------------------------------------------------------
PAPER_SIDE = [  # (t*, S/D)
    (2.0, 0.504), (11.3, 0.597), (21.2, 0.695), (44.0, 0.755),
    (78.0, 0.864), (132.0, 0.953), (197.0, 0.997), (266.0, 1.036),
    (366.0, 1.061), (464.0, 1.101), (666.0, 1.180), (930.0, 1.249),
]
PAPER_FRONT = [  # (t*, S/D)
    (6.2, 0.303), (12.0, 0.45), (22.0, 0.50), (45.0, 0.579),
    (68.0, 0.627), (91.0, 0.678), (133.0, 0.806), (201.0, 0.954),
    (267.0, 1.053), (367.0, 1.130), (465.0, 1.200), (668.0, 1.318),
    (931.0, 1.347),
]

SETS = ("front", "sideL", "sideR")


def read_profile(path):
    """Return (z, alpha) lists from a sampled-sets csv file."""
    with open(path, newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and r[0].strip()]
    if not rows:
        return [], []
    header = [c.strip() for c in rows[0]]
    try:
        float(header[0])            # no header line
        icoord, ialpha = 0, len(rows[0]) - 1
        data = rows
    except ValueError:
        names = [h.lower() for h in header]
        icoord = names.index("z") if "z" in names else 0
        ialpha = next(i for i, n in enumerate(names) if "alpha" in n)
        data = rows[1:]
    z, a = [], []
    for r in data:
        z.append(float(r[icoord]))
        a.append(float(r[ialpha]))
    return z, a


def bed_elevation(z, a, alpha_c):
    """Highest z where alpha crosses alpha_c (profiles are z-ascending)."""
    for i in range(len(z) - 1, 0, -1):
        lo, hi = a[i - 1], a[i]
        if lo >= alpha_c > hi:
            return z[i - 1] + (alpha_c - lo) * (z[i] - z[i - 1]) / (hi - lo)
    if a and a[-1] >= alpha_c:
        return z[-1]
    return float("nan")


def collect(case, alpha_c):
    base = os.path.join(case, "postProcessing", "bedLevels")
    times = []
    for d in glob.glob(os.path.join(base, "*")):
        try:
            times.append((float(os.path.basename(d)), d))
        except ValueError:
            pass
    times.sort()
    if not times:
        sys.exit(f"no data under {base} - has the scour stage run?")
    series = []
    for t, d in times:
        row = {"t": t}
        for name in SETS:
            hits = glob.glob(os.path.join(d, name + "_*"))
            if not hits:
                row[name] = float("nan")
                continue
            z, a = read_profile(hits[0])
            row[name] = bed_elevation(z, a, alpha_c)
        series.append(row)
    return series


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--t0", type=float, default=0.0,
                   help="experimental t=0 in simulation time (default 0: "
                        "the precursor workflow starts scour at t_sim = 0)")
    p.add_argument("--alpha-c", type=float, default=0.5,
                   help="alpha.a defining the bed interface (default 0.5)")
    p.add_argument("--case", default=".", help="case directory")
    args = p.parse_args()

    series = collect(args.case, args.alpha_c)

    ref = next((r for r in series if r["t"] >= args.t0 - 1e-6), series[0])
    if abs(ref["t"] - args.t0) > 2.0:
        print(f"WARNING: reference time {ref['t']} s is far from --t0 "
              f"{args.t0} s; scour depths use it as the zero level anyway.")

    out = os.path.join(args.case, "scour_timeseries.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t_sim_s", "t_exp_s", "t_star",
                    "S_front_mm", "S_sideL_mm", "S_sideR_mm", "S_side_mean_mm",
                    "S_front/D", "S_side_mean/D"])
        for r in series:
            if r["t"] < ref["t"]:
                continue
            te = r["t"] - args.t0
            s = {}
            for name in SETS:
                s[name] = (ref[name] - r[name]) * 1000.0  # mm, positive down
            side = [v for v in (s["sideL"], s["sideR"]) if not math.isnan(v)]
            smean = sum(side) / len(side) if side else float("nan")
            w.writerow([f"{r['t']:.3f}", f"{te:.3f}", f"{te*TSTAR_PER_SEC:.3f}",
                        f"{s['front']:.3f}", f"{s['sideL']:.3f}",
                        f"{s['sideR']:.3f}", f"{smean:.3f}",
                        f"{s['front']/D/1000:.4f}", f"{smean/D/1000:.4f}"])
    print(f"wrote {out}")

    # quick comparison at the paper's early instants
    print("\ncomparison with Li et al. (2020), Fig. 5 (digitized):")
    print("  t_exp [s]  t*    paper side [mm]  paper front [mm]")
    print("      54     2         ~20.2            ~12 (first record t*=2-6)")
    print("     298    11         ~23.9            ~13-18")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available - skipping plot")
        return

    ts, sf, ss = [], [], []
    for r in series:
        if r["t"] < ref["t"]:
            continue
        te = r["t"] - args.t0
        ts.append(te * TSTAR_PER_SEC)
        sf.append((ref["front"] - r["front"]) * 1000 / (D * 1000))
        side = [(ref[n] - r[n]) * 1000 for n in ("sideL", "sideR")
                if not math.isnan(r[n])]
        ss.append(sum(side) / len(side) / (D * 1000) if side else float("nan"))

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ts, ss, "-", color="tab:blue", label="sim: pier side")
    ax.plot(ts, sf, "-", color="tab:orange", label="sim: pier front")
    ax.plot(*zip(*PAPER_SIDE), "o", mfc="none", color="tab:blue",
            label="exp: pier side (Fig. 5)")
    ax.plot(*zip(*PAPER_FRONT), "*", color="tab:orange",
            label="exp: pier front (Fig. 5)")
    ax.set_xlabel("t*")
    ax.set_ylabel("S/D")
    ax.set_xlim(0, max(15, max(ts) * 1.1 if ts else 15))
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    png = os.path.join(args.case, "scour_vs_paper.png")
    fig.savefig(png, dpi=150)
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
