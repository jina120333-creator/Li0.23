#!/usr/bin/env python3
"""Check spin-up convergence of the approach flow from the 'approachFlow'
functionObject (vertical U.b/k.b profile at x = -0.4 m, 10D upstream).

For every sampled time this prints:
  - depth-averaged streamwise velocity  (target: U0 = 0.233 m/s)
  - friction velocity u* from a log-law fit over 0.002 < z < 0.02 m
    (target: u* = 0.016 m/s, the paper's value; this controls the Shields
    number and therefore the scour rate in this clear-water case)

The spin-up can be considered converged once both values are steady and
close to the targets. If u* settles well below 0.016 m/s the scour stage
WILL under-predict the scour rate regardless of the sediment model.

Usage:  python3 scripts/check_approach_flow.py [--case DIR]
"""

import argparse
import csv
import glob
import math
import os
import sys

KAPPA = 0.41
U0_TARGET = 0.233
USTAR_TARGET = 0.016


def read_profile(path):
    """Return (z, Ux) from a sampled-sets csv file (vector field U.b)."""
    with open(path, newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and r[0].strip()]
    if not rows:
        return [], []
    header = [c.strip().lower() for c in rows[0]]
    try:
        float(rows[0][0])
        icoord, iux = 0, 1          # headerless: coord, Ux, Uy, Uz, ...
        data = rows
    except ValueError:
        icoord = header.index("z") if "z" in header else 0
        iux = next(i for i, n in enumerate(header)
                   if n.startswith("u") and (n.endswith("x") or n.endswith("0")))
        data = rows[1:]
    z, u = [], []
    for r in data:
        z.append(float(r[icoord]))
        u.append(float(r[iux]))
    return z, u


def depth_average(z, u):
    s = 0.0
    for i in range(1, len(z)):
        s += 0.5 * (u[i] + u[i - 1]) * (z[i] - z[i - 1])
    return s / (z[-1] - z[0])


def ustar_loglaw(z, u, zmin=0.002, zmax=0.02):
    """u* from linear regression of U on ln(z): slope = u*/kappa."""
    pts = [(math.log(zi), ui) for zi, ui in zip(z, u) if zmin <= zi <= zmax]
    if len(pts) < 3:
        return float("nan")
    n = len(pts)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return slope * KAPPA


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--case", default=".", help="case directory")
    args = p.parse_args()

    base = os.path.join(args.case, "postProcessing", "approachFlow")
    times = []
    for d in glob.glob(os.path.join(base, "*")):
        try:
            times.append((float(os.path.basename(d)), d))
        except ValueError:
            pass
    times.sort()
    if not times:
        sys.exit(f"no data under {base} - has the run started?")

    print(f"approach flow at x = -0.4 m   "
          f"(targets: U_avg = {U0_TARGET} m/s, u* = {USTAR_TARGET} m/s)\n")
    print("   t [s]    U_avg [m/s]    u* [m/s]")
    for t, d in times:
        hits = glob.glob(os.path.join(d, "approach*"))
        if not hits:
            continue
        z, u = read_profile(hits[0])
        if len(z) < 3:
            continue
        print(f"  {t:7.1f}    {depth_average(z, u):9.4f}    "
              f"{ustar_loglaw(z, u):8.4f}")

    print("\nBoth columns steady and near targets -> spin-up converged;")
    print("that time is a safe t0 (= experimental t = 0) for the scour stage.")


if __name__ == "__main__":
    main()
