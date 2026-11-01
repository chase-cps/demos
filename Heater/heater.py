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
  4. The C function in heater.c is the thermostat, called once per step.
     It implements Thermostat with theta = 74, not with theta = 76: each
     step is a call, so ESBMC (or CBMC) checks one call against the formula
     of one step of Thermostat. Asked the other way, the repair finds the
     theta that the code implements: 74.
  5. Between the samples: one step is 20 s, and the temperature changes at
     most 0.1 degree per second (2 degrees per step). With theta = 74 the
     samples reach 75, and the check in continuous time does not show the
     refinement (unknown: the margin of 2 degrees is a sufficient
     condition, not a counterexample). With theta = 71 the samples stay at
     72 or below, and the refinement holds at every instant.

The page out/heater.html draws the room and the thermostat inside Comfort,
the thermostat with its C code, with theta = 76 (red) and theta = 74
(green).

    python heater.py
    python heater.py --expect     # exit code 1 when a result is not the expected one

Steps 1 to 3 need z3; step 4 needs ESBMC or CBMC.
"""

import os
import sys

import tempfile

from chase_cps import (CFunction, Component, System, is_implementation, load_spec, minimize,
                       refines, repair, sampled, viz)

HERE = os.path.dirname(os.path.abspath(__file__))
PERIOD, RATES = 20, {"T": 0.1, "theta": 0, "tmax": 0}     # 20 s a step; T changes at most 0.1 degree/s


def continuous(theta):
    """Room and Thermostat refine Comfort at every instant between the
    samples, with theta (as chase-cps check heater.ltl --period 20
    --lipschitz T=0.1 tmax=0 --refines Room+Thermostat Comfort)."""
    with open(os.path.join(HERE, "heater.ltl"), encoding="utf-8") as f:
        text = f.read().replace("integer constant theta 76;", f"integer constant theta {theta};")
    read = []
    for a, g, used in (("show", "known", ("Room", "Thermostat")), ("known", "show", ("Comfort",))):
        changed, refused = sampled.spec(text, RATES, PERIOD, a, g)    # the parts know their guarantees,
        assert not set(used) & set(refused), refused                  # the requirement shows its own
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "heater.ltl")
            with open(copy, "w", encoding="utf-8") as f:
                f.write(changed)
            read.append(load_spec(copy))
    parts, req = read
    return sampled.not_shown(refines(parts["Room"].compose(parts["Thermostat"]), req["Comfort"])).status


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
    thermostat = c["Thermostat"]
    show(4, "heater.c, called once per step, implements Thermostat with theta = 74",
         is_implementation(f, thermostat.instantiate({"theta": 74})).status, "valid")
    show(4, "heater.c implements Thermostat with theta = 76",
         is_implementation(f, thermostat).status, "invalid")
    r = repair("impl", f, thermostat, parameters={"theta": (0, 200, "int")})
    show(4, "the theta that the code implements", r.values, {"theta": 74})
    show(5, "with theta = 74, the refinement between the samples (20 s, 0.1 degree/s)", continuous(74), "unknown")
    show(5, "with theta = 71, the refinement between the samples", continuous(71), "valid")
    # the page: before and after the repair, the thermostat with its code
    pairs = []
    for theta in (76, 74):
        part = thermostat.instantiate({"theta": theta})
        both = c["Room"].compose(part)
        req = comfort.instantiate({}, name="Comfort" if theta == 76 else "Comfort_repaired")
        step = System("Room and thermostat", [Component("Room", c["Room"]),
                                              Component("Thermostat", part, f, status=is_implementation(f, part))])
        pairs.append((step, req, refines(both, req)))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=pairs, open=[b for _, b, _ in pairs] + [k.components[1] for k, _, _ in pairs],
                                title="Heater: before and after the repair"),
                    os.path.join(HERE, "out", "heater.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    import importlib.util
    if importlib.util.find_spec("z3") is None:      # the repair and the formulas over reals
        sys.exit('This demo needs z3: pip install "chase-cps[z3]"')
    sys.exit(main("--expect" in sys.argv))
