"""Charging station: finding and fixing the problems of the requirements.

Two robots share a charging station through an arbiter. charger.ltl has the
contracts of the robots, of four arbiters, and of the whole system. This
script follows one design iteration with the CHASE Python package
(pip install chase-cps):

  1. The Greedy arbiter grants each request at the next step and never
     grants both robots: it is unrealizable, and the unrealizable core gives
     the three guarantees in conflict. Its composition with the robots
     refines System all the same: refinement does not see the conflict.
  2. The Fair arbiter grants each request eventually: it is realizable, and
     a controller is synthesized.
  3. The Pushy arbiter is realizable for a bad reason: it can win by making
     the robots violate its assumptions. The well-separation check finds it,
     and its core gives the two assumptions. The Polite arbiter fixes it.
  4. One guarantee of Fair is implied by another one: remove_vacuous removes
     it and keeps realizability.
  5. The arbiter and the robots feed each other (req and grant). Composed
     with discharge, the assumptions of the robots on the grants are
     discharged by the arbiter: no assumption is left, and the composition
     refines System. (The exact composition refines System too, but its
     assumption is the closed form (A1 & A2) | !(G1 & G2).)

    python charger.py
    python charger.py --expect     # exit code 1 when a result is not the expected one

The checks need slugs (realizability, synthesis, well-separation) and nuXmv
or NuSMV (vacuity, discharge, refinement).
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import (load_spec, is_realizable, synthesize, is_well_separated,
                       remove_vacuous, refines, ltl)

HERE = os.path.dirname(os.path.abspath(__file__))


def terms(formulas) -> str:
    return "\n".join("      " + ltl.to_str(f) for f in formulas)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    c = load_spec(os.path.join(HERE, "charger.ltl"))
    t = args.timeout
    wrong = []

    def step(title, expected, run):
        start = time.time()
        status, text = run()
        seconds = time.time() - start
        mark = "" if status == expected else f"   (expected {expected})"
        print(f"\n{title}: {status} [{seconds:.1f} s]{mark}")
        if text:
            print(text)
        if status != expected:
            wrong.append(title)

    def greedy():
        r = is_realizable(c["Greedy"], core=True, timeout=t)
        text = ""
        if r.core is not None and r.core.status == "found":
            text = "   unrealizable core:\n" + terms(r.core.core.guarantees)
        return r.status, text
    step("1. Greedy is realizable", "unrealizable", greedy)

    def greedy_system():
        g = c["Greedy"].compose(c["Robot1"]).compose(c["Robot2"])
        return refines(g, c["System"], timeout=t).status, ""
    step("   Greedy, Robot1, Robot2 refine System", "valid", greedy_system)

    def fair():
        r = synthesize(c["Fair"], timeout=t)
        text = ""
        if r.controller is not None:
            text = f"   controller with {len(r.controller['nodes'])} states"
        return r.status, text
    step("2. Fair is realizable", "realizable", fair)

    def pushy():
        r = is_well_separated(c["Pushy"], core=True, timeout=t)
        text = ""
        if r.core is not None and r.core.status == "found":
            text = ("   the arbiter can force a violation of these assumptions:\n"
                    + terms(r.core.core.assumptions))
        return r.status, text
    step("3. Pushy is well separated", "not_separated", pushy)
    step("   Polite is well separated", "separated",
         lambda: (is_well_separated(c["Polite"], timeout=t).status, ""))

    def vacuous():
        v = remove_vacuous(c["Fair"], core=True, timeout=t)
        text = "\n".join(f"   removed {x.part} {ltl.to_str(x.term)} ({x.kind}),"
                         f" implied by {', '.join(ltl.to_str(f) for f in x.core or [])}"
                         for x in v.removed)
        return f"{len(v.removed)} removed", text
    step("4. Vacuous terms of Fair", "1 removed", vacuous)

    def composition():
        fair = remove_vacuous(c["Fair"], timeout=t).contract
        charging = fair.compose(c["Robot1"], discharge=True, timeout=t)
        charging = charging.compose(c["Robot2"], name="Charging", discharge=True, timeout=t)
        r = refines(charging, c["System"], timeout=t)
        text = ("   composition with discharge:\n   assumptions:\n"
                + (terms(charging.assumptions) or "      (none)")
                + f"\n   {len(charging.guarantees)} guarantees")
        return r.status, text
    step("5. Fair, Robot1, Robot2 refine System", "valid", composition)

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
