"""Warehouse: the contract of a controller to delegate.

The question: the local controller of a warehouse robot is given to a
designer (a person, or a language model) while perception and localization
stay as they are. What must the controller satisfy for the robot to meet the
requirements of the system?

The example is simplified from S. S. Damera, R. Matheu, and J. S. Baras,
"Contract-Based Agentic Systems Engineering: Delegation as Quotient for
Assured System Design" (arXiv 2610.33349, 2026), with their bounds
(requirements.txt). The controller commands the yaw rate w and the rest at
the dock; it sees the clearance to a worker and the distance to the dock
only as perception and localization report them (c_rep, e_est). This script
follows the delegation with the CHASE Python package (pip install
chase-cps):

  1. Q = System / (Perception || Localization) is the contract of the
     controller: the weakest one with which the system meets its
     requirements. With discharge it keeps the terms: it guarantees the
     requirements of the system and the assumption of perception on the yaw
     rate, |w| <= 0.8 (localization assumes |w| <= 1.0, which is implied).
  2. MissionOnly, the requirements of the system written on what the
     controller sees, does not refine Q: the counterexample keeps the
     reported clearance at 0.40 while the true one is lower.
  3. Margins, which adds the errors of perception and localization to the
     bounds, does not refine Q either: the counterexample turns faster than
     perception allows, and perception no longer bounds its error.
  4. Dispatched, Margins with |w| <= 0.8, refines Q, so Perception ||
     Localization || Dispatched refines System.

    python warehouse.py
    python warehouse.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv: the variables are real numbers, which nuXmv checks
with its SMT engine (go_msat).
"""

from __future__ import annotations

import argparse
import sys
import time

from chase_cps import Contract, ltl, refines

REAL = "real"
YAW = ("w", "c_true", "c_rep", "e_true", "e_est")

PERCEPTION = Contract.from_strings(
    name="Perception", inputs={"w": REAL, "c_true": REAL}, outputs={"c_rep": REAL},
    assumptions=["G (w <= 0.8 & w >= -0.8)"],                  # PA1
    guarantees=["G (c_rep <= c_true + 0.3)"])                    # PG1
LOCALIZATION = Contract.from_strings(
    name="Localization", inputs={"w": REAL, "e_true": REAL}, outputs={"e_est": REAL},
    assumptions=["G (w <= 1.0 & w >= -1.0)"],                  # LA1
    guarantees=["G (e_true <= e_est + 0.05)"])                   # LG1
SYSTEM = Contract.from_strings(
    name="System", inputs={"c_true": REAL, "e_true": REAL},
    outputs={"w": REAL, "rest": "bool", "c_rep": REAL, "e_est": REAL},
    guarantees=["G (c_true >= 0.4)",                             # SG1
                "F (rest & e_true <= 0.1)"])                     # SG2

CONTROLLER = {"inputs": {"c_rep": REAL, "e_est": REAL}, "outputs": {"w": REAL, "rest": "bool"}}
MISSION_ONLY = Contract.from_strings(
    name="MissionOnly", **CONTROLLER,
    guarantees=["G (c_rep >= 0.4)", "F (rest & e_est <= 0.1)"])
MARGINS = Contract.from_strings(
    name="Margins", **CONTROLLER,
    guarantees=["G (c_rep >= 0.7)", "F (rest & e_est <= 0.05)"])
DISPATCHED = Contract.from_strings(
    name="Dispatched", **CONTROLLER,
    guarantees=["G (c_rep >= 0.7)", "F (rest & e_est <= 0.05)", "G (w <= 0.8 & w >= -0.8)"])


def show(trace) -> None:
    """The steps of a counterexample, one line per step."""
    for i, s in enumerate(trace.prefix + trace.loop):
        loop = "   <- the loop starts" if trace.loop and i == len(trace.prefix) else ""
        values = "  ".join(f"{x} = {float(s[x]):5.2f}" for x in YAW if x in s)
        print(f"     {i}: {values}  rest = {bool(s.get('rest'))}{loop}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    t = args.timeout
    wrong = []

    def step(title, expected, run, counterexample=False):
        start = time.time()
        r = run()
        mark = "" if r.status == expected else f"   (expected {expected})"
        print(f"\n{title}: {r.status} [{time.time() - start:.1f} s, reals: {r.reals}]{mark}")
        if counterexample and r.guarantees.trace is not None:
            print("   a counterexample:")
            show(r.guarantees.trace)
        if r.status != expected:
            wrong.append(title)

    fixed = PERCEPTION.compose(LOCALIZATION, name="Fixed", discharge=True, timeout=t)
    q = SYSTEM.divide(fixed, name="Q", discharge=True, timeout=t)
    print("1. Q = System / (Perception || Localization)")
    print("   assumes:")
    for a in q.assumptions:
        print("      " + ltl.to_str(a))
    print("   guarantees:")
    for g in q.guarantees:
        print("      " + ltl.to_str(g))

    step("2. MissionOnly refines Q", "invalid", lambda: refines(MISSION_ONLY, q, timeout=t),
         counterexample=True)
    step("3. Margins refines Q", "invalid", lambda: refines(MARGINS, q, timeout=t),
         counterexample=True)
    step("4. Dispatched refines Q", "valid", lambda: refines(DISPATCHED, q, timeout=t))
    step("   Perception || Localization || Dispatched refines System", "valid",
         lambda: refines(fixed.compose(DISPATCHED, name="Robot", discharge=True, timeout=t),
                         SYSTEM, timeout=t))

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
