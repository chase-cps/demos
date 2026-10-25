"""Plot the results of scaling.py: check time against the number of joints.

    python plot_scaling.py results/scaling.csv results/scaling_discharge.csv

For each file, one line for the refinement check of the correct contracts
and one for the counterexample of the broken version; for a file made with
--discharge, also the composition and refinement time together. The time axis is logarithmic. A check
that did not finish is drawn at the timeout with an empty marker.
"""

from __future__ import annotations

import argparse
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def series(rows, time_key, verdict_key, timeout):
    done, timed_out = [], []
    for r in rows:
        if not r[time_key]:
            continue
        n = int(r["N"])
        if r[verdict_key] == "timeout":
            timed_out.append((n, timeout))
        else:
            done.append((n, float(r[time_key])))
    return done, timed_out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv", nargs="*", default=["results/scaling.csv"],
                   help="CSV files of scaling.py, e.g. one with --discharge")
    p.add_argument("-o", "--output", default="results/scaling.pdf")
    p.add_argument("--timeout", type=float, default=600,
                   help="the timeout used by scaling.py (default 600)")
    args = p.parse_args(argv)

    fig, ax = plt.subplots(figsize=(5, 4.2))
    ticks = set()
    for path in args.csv:
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        ticks |= {int(r["N"]) for r in rows}
        how = rows[0].get("composition", "closed")
        for r in rows:
            if r["compose_s"] and r["refine_s"]:
                r["total_s"] = str(float(r["compose_s"]) + float(r["refine_s"]))
        lines = [("refine_s", "verdict", "refinement", "o"),
                 ("cex_s", "cex_verdict", "counterexample", "s")]
        if how == "discharge":
            lines.append(("total_s", "verdict", "composition + refinement", "^"))
        for time_key, verdict_key, label, marker in lines:
            done, timed_out = series(rows, time_key, verdict_key, args.timeout)
            if not done and not timed_out:
                continue
            line, = ax.plot([n for n, _ in done], [t for _, t in done], marker=marker,
                            linestyle="-" if how == "closed" else ":",
                            label=f"{label} ({how})")
            if timed_out:
                ax.plot([n for n, _ in timed_out], [t for _, t in timed_out], marker=marker,
                        linestyle="none", markerfacecolor="none", color=line.get_color())
    ax.axhline(args.timeout, color="gray", linewidth=0.8, linestyle="--")
    ax.text(1, args.timeout * 1.1, f"timeout of one check ({args.timeout:g} s)", color="gray", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("number of joints N")
    ax.set_ylabel("time (s)")
    ax.set_xticks(sorted(ticks))
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
