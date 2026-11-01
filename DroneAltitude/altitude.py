"""DroneAltitude: a drone climbs to its drop altitude in the wind (signal temporal logic).

A drone of the fire-suppression mission of ContrACT (MDFS) climbs to the
altitude r (20 m) where it drops its water, in a wind of at most wmax per
step (the updraft of the fire). altitude.ltl has the contracts, in signal
temporal logic in discrete time: Drone (h' = h + v + w), Climb (a climb
rate proportional to the error, at most vmax), and the requirement Hover:
within eps of r from some step of the first 10 on, for 5 steps, and never
above r + eps. z3 checks them (pip install chase-cps[z3]):

  1. In a wind of 0.5, the drone meets Hover (eps = 2); in a wind of 1 it
     does not: the gusts keep it more than 2 below r. The worst case of
     the requirement, its smallest robustness, says by how much.
  2. Repair the controller: no climb rate vmax works (impossible). Below
     the target the error goes e' = e/2 + 1, which tends to 2 and stays
     above it: the controller alone cannot meet eps = 2.
  3. Repair the requirement (with the consent of whoever wrote it): the
     least tolerance is eps = 2.5; or, with eps = 2, the strongest wind is
     wmax = 17/21 (about 0.81). Both checked on each side of the bound.
  4. Both constants at once, with a cost that weighs them: (eps - 2) +
     w (1 - wmax), a change of the wind counting w times a change of the
     tolerance. With w = 2, the repair lowers the wind (wmax = 17/21, cost
     8/21); with w = 3, it widens the tolerance (eps = 2.5, cost 1/2).

The page out/altitude.html draws the drone inside Hover in a wind of 1
(red) and with eps = 2.5 (green).

    python altitude.py
    python altitude.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys
from fractions import Fraction

from chase_cps import load_spec, minimize, refines, repair, viz

HERE = os.path.dirname(os.path.abspath(__file__))
HOVER = "F[0,10] G[0,5] (h >= 20 - 2 & h <= 20 + 2) & G[0,15] (h <= 20 + 2)"


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "altitude.ltl"))
    drone = c["Drone"].compose(c["Climb"])
    hover = c["Hover"]
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    calm = hover.instantiate({"wmax": Fraction(1, 2)})
    show(1, "the drone meets Hover in a wind of 0.5", refines(drone, calm).status, "valid")
    show(1, "the drone meets Hover in a wind of 1", refines(drone, hover).status, "invalid")
    for wind, want in (("1", -0.5), ("0.5", 0.75)):
        worst = minimize(HOVER, [drone.assumption, drone.guarantee, f"G[0,15] (w <= {wind} & w + {wind} >= 0)"],
                         {**drone.variables, "w": "real"})
        show(1, f"the worst robustness of Hover in a wind of {wind}", float(worst.value), want)

    r = repair("refines", drone, hover, parameters={"vmax": (0, 10)})
    show(2, "repair the climb rate vmax", r.status, "impossible")

    r = repair("refines", drone, hover, parameters={"eps": (0, 10)}, minimize="eps")
    show(3, "the least tolerance eps", r.values.get("eps"), Fraction(5, 2))
    r = repair("refines", drone, hover, parameters={"wmax": (0, 2)}, maximize="wmax")
    show(3, "the strongest wind wmax with eps = 2", r.values.get("wmax"), Fraction(17, 21))
    for name, value, want in (("eps", Fraction(5, 2), "valid"), ("eps", Fraction(249, 100), "invalid"),
                              ("wmax", Fraction(17, 21), "valid"), ("wmax", Fraction(82, 100), "invalid")):
        show(3, f"{name} = {value}", refines(drone, hover.instantiate({name: value})).status, want)

    for w, want in ((2, {"eps": 2, "wmax": Fraction(17, 21)}), (3, {"eps": Fraction(5, 2), "wmax": 1})):
        # the cost (eps - 2) + w (1 - wmax), written expanded
        r = repair("refines", drone, hover, parameters={"eps": (2, 10), "wmax": (0, 1)},
                   minimize=f"eps - 2 + {w} - {w} * wmax")
        show(4, f"eps and wmax together, a change of the wind weighing {w}", r.values, want)
        print(f"   cost {r.cost}, optimal {r.optimal}, {r.method} in {r.rounds} rounds")

    loose = hover.instantiate({"eps": Fraction(5, 2)}, name="Hover_eps")
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=[(drone, hover), (drone, loose, refines(drone, loose))],
                                open=[hover, loose, c["Climb"]],
                                title="DroneAltitude: the climb in a wind of 1, before and after the repair"),
                    os.path.join(HERE, "out", "altitude.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
