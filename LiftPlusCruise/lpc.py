"""Lift-Plus-Cruise: requirements of NASA with real variables.

lpc.ltl has the requirements of the LPC_mini project of the FRET case study
Lift-Plus-Cruise (requirements.txt), as three contracts of the vehicle:
Vehicle has all the requirements but the two LPC_REACH_HOVER ones, Reach12
and Reach06 have one each. All the variables are outputs of the vehicle,
so the requirements are realizable when they are consistent. With the CHASE
Python package (pip install chase-cps) this script checks:

  1. Vehicle and Reach12 are consistent, and a behavior is printed: kias
     goes down from 120 and the vehicle reaches the hover mode within 12
     steps;
  2. Vehicle and Reach06 are not consistent: kias changes by 10 at most at
     each step, so the vehicle cannot slow down from 120 enough in 6 steps.
     The unsat core gives the requirements in conflict, by name.

These are the results that FRET gives for the two subsets with its
realizability checker (LPC_instructions.md of the case study). The checks
need nuXmv: the requirements compare kias at two steps, which nuXmv checks
with its SMT engine (go_msat). lpc.chase does the same checks with
logics_tool (see LiftPlusCruise.md).

    python lpc.py
    python lpc.py --expect     # exit code 1 when a result is not the expected one
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

from chase_cps import Contract, load_spec, is_consistent

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "lpc.ltl")
MODES = ["thrust_borne", "semi_thrust_borne", "semi_wing_borne", "wing_borne"]


def names(path: str) -> dict[str, list[str]]:
    """The name of each guarantee of each contract: the comment at the end
    of its line in the specification file."""
    out, contract = {}, None
    for line in open(path):
        m = re.match(r"CONTRACT (\w+):", line)
        if m:
            contract = m.group(1)
            out[contract] = []
        m = re.search(r";\s*# (\w+)\s*$", line)
        if m and contract:
            out[contract].append(m.group(1))
    return out


def vehicle(contracts, reach: str) -> tuple[Contract, dict[str, str]]:
    """Vehicle with the guarantee of the contract reach, and the name of the
    requirement of each guarantee."""
    tags = names(SPEC)
    terms = {}
    for c in ("Vehicle", reach):
        assert len(contracts[c].guarantees) == len(tags[c]), f"names of {c} in {SPEC}"
        terms.update({str(g): n for g, n in zip(contracts[c].guarantees, tags[c])})
    v = contracts["Vehicle"]
    c = Contract(f"Vehicle_{reach}", dict(v.inputs), dict(v.outputs), [],
                 list(v.guarantees) + list(contracts[reach].guarantees))
    return c, terms


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    contracts = load_spec(SPEC)
    wrong = []

    c, _ = vehicle(contracts, "Reach12")
    start = time.time()
    r = is_consistent(c, timeout=args.timeout)
    print(f"1. Vehicle and Reach12 are consistent: {r.status} "
          f"[{time.time() - start:.1f} s, reals: {r.reals}]")
    if r.trace is not None:
        print("   a behavior:")
        for i, s in enumerate(r.trace.prefix + r.trace.loop):
            loop = "   <- the loop starts" if i == len(r.trace.prefix) else ""
            print(f"   {i:3}: kias = {float(s['kias']):6.1f}   {MODES[s['lift_mode']]:17}"
                  f"   hover_control_mode = {s['hover_control_mode']}{loop}")
    if r.status != "sat":
        wrong.append("Reach12")

    c, terms = vehicle(contracts, "Reach06")
    start = time.time()
    r = is_consistent(c, core=True, timeout=args.timeout)
    print(f"\n2. Vehicle and Reach06 are consistent: {r.status} "
          f"[{time.time() - start:.1f} s, reals: {r.reals}]")
    if r.core is not None:
        if r.core.status == "found":
            print(f"   unsat core ({r.core.checks} checks):")
            for name in sorted({terms.get(str(g), str(g)) for g in r.core.core.guarantees}):
                print("      " + name)
        else:
            print(f"   unsat core: {r.core.status} {r.core.reason}")
    if r.status != "unsat":
        wrong.append("Reach06")

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
