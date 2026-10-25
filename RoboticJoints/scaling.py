"""RoboticJoints with N joints: composition and refinement check times.

specs.ltl specifies three joints, each by the same contract, and a contract
Joints for the arm. This script builds the same contracts for N joints with
the CHASE Python package (pip install chase-cps), composes the N joint
contracts, and checks that the composition refines Joints. For N = 3 the
contracts are those of specs.ltl. With --broken it also checks a faulty
version, where Joint1 does not guarantee G F j1_done, and reports the time to
find the counterexample.

    python scaling.py --joints 1 2 3 4 5 6 7 8 --broken --csv results/scaling.csv
    python plot_scaling.py

The checks need nuXmv or NuSMV. The results are printed as a table and
optionally written as CSV, one row per N: the composition time, the
refinement check time and verdict (timeout when a check does not finish),
and with --broken the time to find the counterexample and its length (prefix
plus loop).
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import time

from chase_cps import Contract, refines

ANGLE = (0, 4)
CMD = (0, 2)


def joint_assumptions(i: int) -> list[str]:
    j = f"j{i}"
    return [
        f"!req_{j}",
        f"G (req_{j} & {j}_angle = 0 & {j}_cmd = 2 -> X ({j}_angle = 0))",
        f"G (req_{j} & {j}_cmd = 1 -> {j}_angle' = {j}_angle + 1)",
        f"G (req_{j} & {j}_cmd = 2 -> {j}_angle' + 1 = {j}_angle)",
        f"G (req_{j} & {j}_cmd = 0 -> {j}_angle' = {j}_angle)",
        f"G (req_{j} & {j}_angle = 4 & {j}_cmd = 1 -> X ({j}_angle = 4))",
        f"G (req_{j} & !{j}_done -> X req_{j})",
        f"G (req_{j} -> {j}_dangle' = {j}_dangle)",
        f"G F req_{j}",
        f"G F (req_{j} & {j}_done -> X !req_{j})",
    ]


def joint_guarantees(i: int) -> list[str]:
    j = f"j{i}"
    return [
        f"{j}_cmd = 0",
        f"G ({j}_done | !req_{j} -> X ({j}_cmd = 0))",
        f"G ({j}_angle = {j}_dangle <-> {j}_done)",
        f"G F {j}_done",
    ]


def joint_variables(i: int) -> tuple[dict, dict]:
    j = f"j{i}"
    inputs = {f"{j}_dangle": ANGLE, f"{j}_angle": ANGLE, f"req_{j}": "bool"}
    outputs = {f"{j}_done": "bool", f"{j}_cmd": CMD}
    return inputs, outputs


def joint(i: int, broken: bool = False) -> Contract:
    """The contract of joint i; broken drops the guarantee G F ji_done."""
    inputs, outputs = joint_variables(i)
    guarantees = joint_guarantees(i)
    if broken:
        guarantees = guarantees[:-1]
    return Contract.from_strings(inputs=inputs, outputs=outputs,
                                 assumptions=joint_assumptions(i),
                                 guarantees=guarantees, name=f"Joint{i}")


def arm(n: int) -> Contract:
    """The contract of the arm with n joints (Joints in specs.ltl): the
    assumptions and guarantees of all the joints."""
    inputs, outputs, assumptions, guarantees = {}, {}, [], []
    for i in range(1, n + 1):
        ins, outs = joint_variables(i)
        inputs.update(ins)
        outputs.update(outs)
        assumptions += joint_assumptions(i)
        guarantees += joint_guarantees(i)
    return Contract.from_strings(inputs=inputs, outputs=outputs, assumptions=assumptions,
                                 guarantees=guarantees, name="Joints")


def compose_joints(n: int, broken: bool = False) -> Contract:
    system = joint(1, broken)
    for i in range(2, n + 1):
        system = system.compose(joint(i))
    return system


def backend_version(backend: str) -> str:
    """The version banner of the model checker, e.g. nuXmv 2.2.0."""
    from chase_cps import tools
    name = "nusmv" if backend.startswith("nusmv") else "nuxmv"
    path = tools.find(name)
    if not path:
        return ""
    out = subprocess.run([path, "-int"], input="quit\n", capture_output=True, text=True).stdout
    m = re.search(r"This is (\S+ \S+)", out)
    return m.group(1) if m else ""


def check(n: int, broken: bool, backend: str, timeout: float):
    start = time.monotonic()
    system = compose_joints(n, broken)
    composed = time.monotonic() - start
    r = refines(system, arm(n), backend, timeout=timeout)
    seconds = r.assumptions.seconds + r.guarantees.seconds
    verdict = r.status
    if verdict == "unknown" and "timeout" in (r.assumptions.reason or "") + (r.guarantees.reason or ""):
        verdict = "timeout"
    return r, composed, seconds, verdict


def run(n: int, broken: bool, backend: str, timeout: float) -> dict:
    """One row: the correct version, then the broken one with --broken."""
    r, composed, seconds, verdict = check(n, False, backend, timeout)
    used = r.guarantees.backend or r.assumptions.backend or ""
    row = {"N": n, "compose_s": round(composed, 3), "refine_s": round(seconds, 3),
           "verdict": verdict, "cex_s": "", "cex_length": "", "cex_verdict": "",
           "backend": used, "backend_version": backend_version(used)}
    if broken:
        r, _, seconds, verdict = check(n, True, backend, timeout)
        part = r.assumptions if r.failed == "assumptions" else r.guarantees
        row["cex_s"] = round(seconds, 3)
        row["cex_verdict"] = verdict
        if part.trace:
            row["cex_length"] = len(part.trace.prefix) + len(part.trace.loop)
    return row


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--joints", type=int, nargs="+", default=[1, 2, 3])
    p.add_argument("--backend", default="auto", choices=["auto", "nuxmv", "nusmv"])
    p.add_argument("--timeout", type=float, default=600,
                   help="seconds for each implication check (default 600)")
    p.add_argument("--broken", action="store_true",
                   help="also check the version where Joint1 lacks G F j1_done")
    p.add_argument("--csv", help="write the results to this file")
    p.add_argument("--expect", action="store_true",
                   help="exit with 1 unless every correct version is valid and every "
                        "broken one invalid (for CI)")
    args = p.parse_args(argv)

    rows = []
    print(f"{'N':>3} {'compose_s':>9} {'refine_s':>9} {'verdict':>8} {'cex_s':>8} "
          f"{'cex_length':>10} {'backend':>10}")
    for n in args.joints:
        row = run(n, args.broken, args.backend, args.timeout)
        rows.append(row)
        print(f"{row['N']:>3} {row['compose_s']:>9} {row['refine_s']:>9} {row['verdict']:>8} "
              f"{row['cex_s']:>8} {row['cex_length']:>10} {row['backend']:>10}", flush=True)
        if args.csv:
            with open(args.csv, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    if args.expect and any(r["verdict"] != "valid" or (args.broken and r["cex_verdict"] != "invalid")
                           for r in rows):
        print("unexpected verdict", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
