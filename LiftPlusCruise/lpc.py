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
realizability checker (LPC_instructions.md of the case study). Consistency
says that some behavior hovers within 12 steps, not that every one does.
The next steps ask what makes the vehicle hover: the requirements are split
between two components, the mode logic (lift_mode, from the speeds and the
hover control mode) and the pilot (kias, kgs, hover_control_mode).

  3. ModeLogic || Pilot refines Vehicle: the split keeps the requirements.
  4. Q12 = Reach12 / ModeLogic is what the pilot must do for the vehicle to
     hover within 12 steps. Pilot, with the requirements alone, does not
     refine it: kias may stay at 120.
  5. Slow, a pilot that slows down by 10 at each step, does not refine it
     either: the hover control mode is never on, and the vehicle stays semi
     thrust borne.
  6. Decel, which also turns the hover control mode on when kgs < 20,
     refines Q12, so ModeLogic || Decel refines Reach12. Decel does not
     refine Q06 = Reach06 / ModeLogic (no pilot does, step 2).

The checks need nuXmv: the requirements compare kias at two steps, which
nuXmv checks with its SMT engine (go_msat). lpc.chase does steps 1 and 2
with logics_tool (see LiftPlusCruise.md).

    python lpc.py
    python lpc.py --expect     # exit code 1 when a result is not the expected one
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

from chase_cps import Contract, load_spec, is_consistent, refines, viz

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


# The requirements of the pilot; the others are those of the mode logic.
PILOT = ("LPC_INIT_KIAS", "LPC_KIAS_KGS", "LPC_KIAS_DERIVATIVE", "LPC_KIAS_0",
         "LPC_INIT_HOVER_MODE")


def split(contracts) -> tuple[Contract, Contract]:
    """Vehicle as two components: the mode logic, which gives lift_mode, and
    the pilot, which gives kias, kgs, and hover_control_mode."""
    v = contracts["Vehicle"]
    pilot = [g for g, n in zip(v.guarantees, names(SPEC)["Vehicle"]) if n in PILOT]
    mode = [g for g, n in zip(v.guarantees, names(SPEC)["Vehicle"]) if n not in PILOT]
    speeds = {x: v.outputs[x] for x in ("kias", "kgs", "hover_control_mode")}
    return (Contract("ModeLogic", speeds, {"lift_mode": v.outputs["lift_mode"]}, [], mode),
            Contract("Pilot", {}, speeds, [], pilot))


def behavior(trace) -> None:
    """The steps of a trace, one line per step."""
    for i, s in enumerate(trace.prefix + trace.loop):
        loop = "   <- the loop starts" if trace.loop and i == len(trace.prefix) else ""
        print(f"   {i:3}: kias = {float(s['kias']):6.1f}   {MODES[s['lift_mode']]:17}"
              f"   hover_control_mode = {s['hover_control_mode']}{loop}")


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
    r = reach12 = is_consistent(c, timeout=args.timeout)
    vehicle12 = c
    print(f"1. Vehicle and Reach12 are consistent: {r.status} "
          f"[{time.time() - start:.1f} s, reals: {r.reals}]")
    if r.trace is not None:
        print("   a behavior:")
        behavior(r.trace)
    if r.status != "sat":
        wrong.append("Reach12")

    c, terms = vehicle(contracts, "Reach06")
    start = time.time()
    r = reach06 = is_consistent(c, core=True, timeout=args.timeout)
    vehicle06 = c
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

    t = args.timeout

    def step(title, expected, run, show=False):
        start = time.time()
        r = run()
        mark = "" if r.status == expected else f"   (expected {expected})"
        print(f"\n{title}: {r.status} [{time.time() - start:.1f} s, reals: {r.reals}]{mark}")
        if show and r.guarantees.trace is not None:
            print("   a counterexample:")
            behavior(r.guarantees.trace)
        if r.status != expected:
            wrong.append(title)
        return r

    mode, pilot = split(contracts)
    both = mode.compose(pilot, name="Split")
    split_vehicle = step("3. ModeLogic || Pilot refines Vehicle", "valid",
                         lambda: refines(both, contracts["Vehicle"], timeout=t))
    q12 = contracts["Reach12"].divide(mode, name="Q12", discharge=True, timeout=t)
    pilot_q12 = step("4. Pilot refines Q12 = Reach12 / ModeLogic", "invalid",
                     lambda: refines(pilot, q12, timeout=t), show=True)
    slow = pilot.ensure("G((kias > 0.0) -> (kias' = kias - 10.0))", name="Slow")
    slow_q12 = step("5. Slow refines Q12", "invalid", lambda: refines(slow, q12, timeout=t),
                    show=True)
    decel = slow.ensure("G(hover_control_mode <-> (kgs < 20.0))", name="Decel")
    decel_q12 = step("6. Decel refines Q12", "valid", lambda: refines(decel, q12, timeout=t))
    step("   ModeLogic || Decel refines Reach12", "valid",
         lambda: refines(mode.compose(decel, name="Hover"), contracts["Reach12"], timeout=t))
    q06 = contracts["Reach06"].divide(mode, name="Q06", discharge=True, timeout=t)
    decel_q06 = step("   Decel refines Q06 = Reach06 / ModeLogic", "invalid",
                     lambda: refines(decel, q06, timeout=t))

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(vehicle12, vehicle06, contracts["Vehicle"], q12,
                                refines=[(both, contracts["Vehicle"], split_vehicle),
                                         (pilot, q12, pilot_q12), (slow, q12, slow_q12),
                                         (decel, q12, decel_q12), (decel, q06, decel_q06)],
                                checks=[(vehicle12, "consistent", reach12),
                                        (vehicle06, "consistent", reach06)],
                                title="Lift-Plus-Cruise: what the pilot must do"),
                    os.path.join(HERE, "out", "lpc.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
