"""Braking: repairing the timing of an emergency braking system.

The braking system of ContrACT (Xiao, Lutz, Castillo-Effen, Nuzzo, MEMOCODE
2026): the pedal path BrakePedal -> PedalProcessing -> Brake1 and the
camera path Camera -> Detection -> Link -> Brake2, where Link is a network
link with the inconsistency kappa (10). braking.ltl has the timing
contracts that ContrACT builds for each node (t: timestamp, d: start, T:
completion), and two system contracts:

- PedalDeadline: Brake 1 starts at most lam_b (4) after its timestamp, given
  the delay of 1 that the camera path can cause it (the offset of
  ContrACT);
- CameraDelay: the camera path delays Brake 1 by at most y_f (0.95, what
  Brake 1 can absorb: 4 - 3.05).

The contracts compare reals without temporal operators, so z3 checks them,
and repair computes the values that fail at once (projection). This script
uses the CHASE Python package (pip install chase-cps[z3]):

  1. The pedal path does not refine PedalDeadline: Brake 1 can start 4.05
     late.
  2. Repair the bound: lam_b = 4.05 (option A of the paper).
  3. Repair the link so that the camera path never delays Brake 1 (y_f = 0):
     kappa = 11 (option B of the paper).
  4. Repair the link so that it delays Brake 1 by at most what Brake 1 can
     absorb (y_f = 0.95): kappa = 10.05, a smaller change. With 10.05 the
     camera path refines CameraDelay; with 10.04 it does not.

The page out/braking.html draws each requirement with the path that must
refine it, before the repair (red) and after it (green).

    python braking.py
    python braking.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys
from fractions import Fraction

from chase_cps import load_spec, refines, repair, viz

HERE = os.path.dirname(os.path.abspath(__file__))


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "braking.ltl"))
    pedal = c["BrakePedal"].compose(c["PedalProcessing"]).compose(c["Brake1"])
    camera = c["Camera"].compose(c["Detection"]).compose(c["Link"]).compose(c["Brake2"])
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    def number(v):
        return float(v) if isinstance(v, Fraction) else v

    show(1, "the pedal path refines PedalDeadline (lam_b = 4)",
         refines(pedal, c["PedalDeadline"]).status, "invalid")
    r = repair("refines", pedal, c["PedalDeadline"], parameters={"lam_b": (0, 10)})
    show(2, "repair lam_b", number(r.values["lam_b"]), 4.05)
    print(f"   optimal {r.optimal}, {r.method}, {r.seconds:.2f} s")

    none = c["CameraDelay"].instantiate({"y_f": 0})
    r = repair("refines", camera, none, parameters={"kappa": (0, 20)})
    show(3, "repair kappa, no delay to Brake 1", number(r.values["kappa"]), 11)

    r = repair("refines", camera, c["CameraDelay"], parameters={"kappa": (0, 20)})
    show(4, "repair kappa, a delay of at most 0.95", number(r.values["kappa"]), 10.05)
    show(4, "kappa = 10.05 refines CameraDelay", refines(
        camera.instantiate({"kappa": Fraction(201, 20)}), c["CameraDelay"]).status, "valid")
    show(4, "kappa = 10.04 refines CameraDelay", refines(
        camera.instantiate({"kappa": Fraction(251, 25)}), c["CameraDelay"]).status, "invalid")
    # the page: before and after each repair
    def paths(lam=None, kappa=None):
        deadline = c["PedalDeadline"] if lam is None else \
            c["PedalDeadline"].instantiate({"lam_b": lam}, name="PedalDeadline_repaired")
        link = c["Link"] if kappa is None else c["Link"].instantiate({"kappa": kappa})
        pedal = c["BrakePedal"].compose(c["PedalProcessing"]).compose(c["Brake1"])
        camera = c["Camera"].compose(c["Detection"]).compose(link).compose(c["Brake2"])
        return pedal, deadline, camera, link
    pairs, links = [], []
    for lam, kappa in ((None, None), (Fraction(81, 20), Fraction(201, 20))):
        pedal, deadline, camera, link = paths(lam, kappa)
        links.append(link)
        delay = c["CameraDelay"] if kappa is None else \
            c["CameraDelay"].instantiate({}, name="CameraDelay_repaired")
        pairs += [(pedal, deadline, refines(pedal, deadline)),
                  (camera, delay, refines(camera, delay))]
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=pairs, open=[b for _, b, _ in pairs] + links,
                                title="Braking: before and after the repair"),
                    os.path.join(HERE, "out", "braking.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
