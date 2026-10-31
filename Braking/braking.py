"""Braking: repairing the timing of an emergency braking system.

The braking system of ContrACT (Xiao, Lutz, Castillo-Effen, Nuzzo, MEMOCODE
2026): the pedal path BrakePedal -> PedalProcessing -> Brake1 and the
camera path Camera -> Detection -> Link -> Brake2, where Link is a network
link with the inconsistency kappa (10). braking.ltl has the timing
contracts that ContrACT builds for each node (t: timestamp, d: start, T:
completion), and two system contracts:

- SysB: Brake 1 starts at most lam_b (4) after its timestamp, given
  the delay of 1 that the camera path can cause it (the offset of
  ContrACT);
- DelayF: the camera path delays Brake 1 by at most y_f (0.95, what Brake 1
  can absorb: 4 - 3.05).

The contracts compare reals without temporal operators, so z3 checks them,
and repair computes the values that fail at once (projection). This script
uses the CHASE Python package (pip install chase-cps[z3]):

  1. The pedal path does not refine SysB: Brake 1 can start 4.05 late.
  2. Repair the bound: lam_b = 4.05 (option A of the paper).
  3. Repair the link so that the camera path never delays Brake 1 (y_f = 0):
     kappa = 11 (option B of the paper).
  4. Repair the link so that it delays Brake 1 by at most what Brake 1 can
     absorb (y_f = 0.95): kappa = 10.05, a smaller change. With 10.05 the
     camera path refines DelayF; with 10.04 it does not.

    python braking.py
    python braking.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys
from fractions import Fraction

from chase_cps import load_spec, refines, repair

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

    show(1, "the pedal path refines SysB (lam_b = 4)", refines(pedal, c["SysB"]).status,
         "invalid")
    r = repair("refines", pedal, c["SysB"], parameters={"lam_b": (0, 10)})
    show(2, "repair lam_b", number(r.values["lam_b"]), 4.05)
    print(f"   optimal {r.optimal}, {r.method}, {r.seconds:.2f} s")

    none = c["DelayF"].instantiate({"y_f": 0})
    r = repair("refines", camera, none, parameters={"kappa": (0, 20)})
    show(3, "repair kappa, no delay to Brake 1", number(r.values["kappa"]), 11)

    r = repair("refines", camera, c["DelayF"], parameters={"kappa": (0, 20)})
    show(4, "repair kappa, a delay of at most 0.95", number(r.values["kappa"]), 10.05)
    show(4, "kappa = 10.05 refines DelayF", refines(
        camera.instantiate({"kappa": Fraction(201, 20)}), c["DelayF"]).status, "valid")
    show(4, "kappa = 10.04 refines DelayF", refines(
        camera.instantiate({"kappa": Fraction(251, 25)}), c["DelayF"]).status, "invalid")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
