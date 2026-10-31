"""Heater: a thermostat that overshoots, repaired, then its code checked.

A room is heated by a thermostat over 10 steps (heater.ltl): the heater adds
u units per step and the room loses 1; the thermostat heats (u = 3) while
the temperature T is below the constant theta (76). The requirement Comfort
says that T stays at most tmax (75). The contracts are in signal temporal
logic in discrete time (G[0,10]), so z3 checks them. This script follows
the design with the CHASE Python package (pip install chase-cps[z3]):

  1. Room and Thermostat composed do not refine Comfort: the counterexample
     heats to 76, cools to 75, and heats again to 77. The worst case of the
     requirement (its smallest robustness over the behaviors of the system)
     is -2: 2 units too hot.
  2. Repair the thermostat: the least change of theta that makes the
     refinement hold is theta = 74. The worst case is then 0: T reaches 75
     and no more.
  3. Or repair the requirement: tmax = 77, the overshoot.
  4. The C function in heater.c is one step of the repaired thermostat
     (ESBMC, or CBMC, checks it against ThermostatStep): it implements the
     step with theta = 74, not with theta = 76. Asked the other way, the
     repair finds the theta that the code implements: 74.

    python heater.py
    python heater.py --expect     # exit code 1 when a result is not the expected one

Steps 1 to 3 need z3; step 4 needs ESBMC or CBMC.
"""

import os
import sys

from chase_cps import CFunction, is_implementation, load_spec, minimize, refines, repair

HERE = os.path.dirname(os.path.abspath(__file__))


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "heater.ltl"))
    system = c["Room"].compose(c["Thermostat"])
    comfort = c["Comfort"]
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    r = refines(system, comfort)
    show(1, "Room and Thermostat refine Comfort", r.status, "invalid")
    worst = minimize("G[0,10] (T <= 75)", system, system.variables)
    show(1, "worst case of T <= 75 over the behaviors (robustness)", worst.value, -2)

    r = repair("refines", system, comfort, parameters={"theta": (60, 90, "int")})
    show(2, "repair theta", r.values, {"theta": 74})
    print(f"   cost {r.cost}, optimal {r.optimal}, {r.method} in {r.rounds} rounds, "
          f"checked by {r.check.guarantees.backend}")
    fixed = system.instantiate(r.values)
    worst = minimize("G[0,10] (T <= 75)", fixed, fixed.variables)
    show(2, "worst case with theta = 74", worst.value, 0)

    r = repair("refines", system, comfort, parameters={"tmax": (60, 90, "int")})
    show(3, "repair tmax instead", r.values, {"tmax": 77})

    f = CFunction(os.path.join(HERE, "heater.c"), "thermostat")
    step = c["ThermostatStep"]
    show(4, "heater.c implements ThermostatStep with theta = 74",
         is_implementation(f, step.instantiate({"theta": 74})).status, "valid")
    show(4, "heater.c implements ThermostatStep with theta = 76",
         is_implementation(f, step).status, "invalid")
    r = repair("impl", f, step, parameters={"theta": (0, 200, "int")})
    show(4, "the theta that the code implements", r.values, {"theta": 74})
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
