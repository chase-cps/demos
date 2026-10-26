"""Lift-Plus-Cruise: requirements of NASA with real variables.

The requirements are those of the LPC_mini project of the FRET case study
Lift-Plus-Cruise (https://github.com/NASA-SW-VnV/fret, caseStudies/
LiftPlusCruise; Pressburger, Katis, Dutle, Mavridou, REFSQ 2023). They give
the lift mode of the aircraft from its airspeed kias and its ground speed
kgs, both real numbers. Each requirement below is written by hand in the
syntax of CHASE from the future time LTL that FRET gives for it
(ftInfAUExpanded); the comment above it is its FRETish text.

In the FRET project all the variables are outputs of the vehicle, so the
requirements are realizable when they are consistent. With the CHASE Python
package (pip install chase-cps) this script checks:

  1. the requirements with LPC_REACH_HOVER_12 are consistent, and a behavior
     is printed: kias goes down from 120 and the vehicle reaches the hover
     mode within 12 steps;
  2. the requirements with LPC_REACH_HOVER_06 are not consistent: kias
     changes by 10 at most at each step, so the vehicle cannot slow down
     from 120 enough in 6 steps. The unsat core gives the requirements in
     conflict.

These are the results that FRET gives for the two subsets with its
realizability checker (LPC_instructions.md). The checks need nuXmv: the
requirements compare kias at two steps, which nuXmv checks with its SMT
engine (go_msat).

    python lpc.py
    python lpc.py --expect     # exit code 1 when a result is not the expected one
"""

from __future__ import annotations

import argparse
import sys
import time

from chase_cps import Contract, is_consistent

# The lift modes.
TB, STB, SWB, WB = 0, 1, 2, 3
MODES = ["thrust_borne", "semi_thrust_borne", "semi_wing_borne", "wing_borne"]

VARIABLES = {"kias": "real", "kgs": "real", "hover_control_mode": "bool",
             "lift_mode": (0, 3)}


def mode(m: int) -> str:
    return f"(lift_mode = {m})"


def upon(trigger: str, response: str) -> str:
    """FRET "upon T the vehicle shall at the next timepoint satisfy R": when
    T becomes true (or holds at the start), R holds at the next step."""
    return (f"G ((!({trigger}) & X ({trigger})) -> X X ({response})) & "
            f"(({trigger}) -> X ({response}))")


def within(n: int, p: str) -> str:
    """FRET "within n ticks satisfy P", F[0,n] P."""
    return " | ".join("X " * i + f"({p})" for i in range(n + 1))


REQUIREMENTS = {
    # Whenever lift_mode = thrust_borne & kgs <= 20.0 & hover_control_mode
    # the vehicle shall at the next timepoint satisfy lift_mode = thrust_borne
    "LPC_TB_STAY_ON_NEXT":
        f"G (({mode(TB)} & kgs <= 20.0 & hover_control_mode) -> X {mode(TB)})",
    # Whenever lift_mode = semi_thrust_borne & kias <= 40.0 & (kgs > 20.0 |
    # !hover_control_mode) the vehicle shall at the next timepoint satisfy
    # lift_mode = semi_thrust_borne
    "LPC_STB_STAY_ON_NEXT":
        f"G (({mode(STB)} & kias <= 40.0 & (kgs > 20.0 | !hover_control_mode)) "
        f"-> X {mode(STB)})",
    # Upon lift_mode = semi_wing_borne & kias <= 30.0 the vehicle shall at the
    # next timepoint satisfy lift_mode = semi_thrust_borne
    "LPC_SWB_TO_STB": upon(f"{mode(SWB)} & kias <= 30.0", mode(STB)),
    # Upon lift_mode = semi_thrust_borne & kias > 40.0 the vehicle shall at
    # the next timepoint satisfy lift_mode = semi_wing_borne
    "LPC_STB_TO_SWB": upon(f"{mode(STB)} & kias > 40.0", mode(SWB)),
    # Upon lift_mode = semi_thrust_borne & hover_control_mode & kgs <= 20.0
    # the vehicle shall at the next timepoint satisfy lift_mode = thrust_borne
    "LPC_STB_TO_TB": upon(f"{mode(STB)} & hover_control_mode & kgs <= 20.0", mode(TB)),
    # Upon lift_mode = semi_wing_borne & kias > 100.0 the vehicle shall at the
    # next timepoint satisfy lift_mode = wing_borne
    "LPC_SWB_TO_WB": upon(f"{mode(SWB)} & kias > 100.0", mode(WB)),
    # Upon lift_mode = thrust_borne & (!hover_control_mode | kgs > 20.0) the
    # vehicle shall at the next timepoint satisfy lift_mode = semi_thrust_borne
    "LPC_TB_TO_STB": upon(f"{mode(TB)} & (!hover_control_mode | kgs > 20.0)", mode(STB)),
    # The vehicle shall immediately satisfy lift_mode = wing_borne <=> kias >= 90.0
    "LPC_INIT_LIFT_MODE": f"{mode(WB)} <-> kias >= 90.0",
    # The vehicle shall always satisfy lift_mode = thrust_borne |
    # lift_mode = semi_thrust_borne | lift_mode = semi_wing_borne |
    # lift_mode = wing_borne
    "LPC_LIFT_MODE": f"G ({mode(TB)} | {mode(STB)} | {mode(SWB)} | {mode(WB)})",
    # The vehicle shall immediately satisfy kias = 120.0
    "LPC_INIT_KIAS": "kias = 120.0",
    # The vehicle shall always satisfy kias = kgs
    "LPC_KIAS_KGS": "G (kias = kgs)",
    # The vehicle shall always satisfy
    # FTP | absReal(preReal(0.0, kias) - kias) <= 10.0
    # (after the first step, kias changes by 10 at most: kias' is the value
    # of kias at the next step)
    "LPC_KIAS_DERIVATIVE": "G (kias' - kias <= 10.0 & kias - kias' <= 10.0)",
    # Upon lift_mode = wing_borne & kias <= 90.0 the vehicle shall at the
    # next timepoint satisfy lift_mode = semi_wing_borne
    "LPC_WB_TO_SWB": upon(f"{mode(WB)} & kias <= 90.0", mode(SWB)),
    # The vehicle shall immediately satisfy hover_control_mode <=> kgs < 20.0
    "LPC_INIT_HOVER_MODE": "hover_control_mode <-> kgs < 20.0",
    # The vehicle shall always satisfy kias >= 0.0
    "LPC_KIAS_0": "G (kias >= 0.0)",
    # Whenever lift_mode = semi_wing_borne & kias <= 100.0 & kias > 30.0 the
    # vehicle shall at the next timepoint satisfy lift_mode = semi_wing_borne
    "LPC_SWB_STAY_ON_NEXT":
        f"G (({mode(SWB)} & kias <= 100.0 & kias > 30.0) -> X {mode(SWB)})",
    # Whenever lift_mode = wing_borne & kias > 90.0 the vehicle shall at the
    # next timepoint satisfy lift_mode = wing_borne
    "LPC_WB_STAY_ON_NEXT": f"G (({mode(WB)} & kias > 90.0) -> X {mode(WB)})",
}

REACH = {
    # The vehicle shall within 12 ticks satisfy lift_mode = thrust_borne
    "LPC_REACH_HOVER_12": within(12, mode(TB)),
    # The vehicle shall within 6 ticks satisfy lift_mode = thrust_borne
    "LPC_REACH_HOVER_06": within(6, mode(TB)),
}


def vehicle(reach: str) -> tuple[Contract, dict[str, str]]:
    """The contract of the vehicle with all the requirements but the two
    LPC_REACH_HOVER ones, and the one named reach; and the requirement of
    each guarantee. Some requirements are split by CHASE at their top
    conjunction into two guarantees."""
    requirements = dict(REQUIREMENTS, **{reach: REACH[reach]})
    c = Contract.from_strings(outputs=VARIABLES, guarantees=list(requirements.values()),
                              name="Vehicle")
    names = {}
    for name, text in requirements.items():
        for g in Contract.from_strings(outputs=VARIABLES, guarantees=[text]).guarantees:
            names[str(g)] = name
    return c, names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    wrong = []

    c, _ = vehicle("LPC_REACH_HOVER_12")
    start = time.time()
    r = is_consistent(c, timeout=args.timeout)
    print(f"1. Requirements with LPC_REACH_HOVER_12 are consistent: {r.status} "
          f"[{time.time() - start:.1f} s, reals: {r.reals}]")
    if r.trace is not None:
        print("   a behavior:")
        for i, s in enumerate(r.trace.prefix + r.trace.loop):
            loop = "   <- the loop starts" if i == len(r.trace.prefix) else ""
            print(f"   {i:3}: kias = {float(s['kias']):6.1f}   {MODES[s['lift_mode']]:17}"
                  f"   hover_control_mode = {s['hover_control_mode']}{loop}")
    if r.status != "sat":
        wrong.append("LPC_REACH_HOVER_12")

    c, names = vehicle("LPC_REACH_HOVER_06")
    start = time.time()
    r = is_consistent(c, core=True, timeout=args.timeout)
    print(f"\n2. Requirements with LPC_REACH_HOVER_06 are consistent: {r.status} "
          f"[{time.time() - start:.1f} s, reals: {r.reals}]")
    if r.core is not None:
        if r.core.status == "found":
            print(f"   unsat core ({r.core.checks} checks):")
            for name in sorted({names.get(str(g), str(g)) for g in r.core.core.guarantees}):
                print("      " + name)
        else:
            print(f"   unsat core: {r.core.status} {r.core.reason}")
    if r.status != "unsat":
        wrong.append("LPC_REACH_HOVER_06")

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
