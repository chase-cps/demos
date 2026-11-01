"""Deadline: the least bound on the waiting time of a request.

A client asks for a resource and keeps asking until it is granted; the
arbiter grants every third step; Wait counts the steps a request has waited
(deadline.ltl). The requirement MaxWait says that no request waits more than
the constant k (1). The formulas are LTL, so nuXmv checks them. This script
uses the CHASE Python package (pip install chase-cps):

  1. Client, Arbiter, and Wait composed do not refine MaxWait: a request can
     wait 2 steps.
  2. repair finds the least k: 2. Each round optimizes k under the
     conditions that the counterexamples found so far are no longer
     counterexamples, then checks the refinement with nuXmv.
  3. Every k from 0 to 9, checked one by one, gives the same answer: 2 is
     the least that passes.

The page out/deadline.html draws the system inside MaxWait with k = 1 (red)
and k = 2 (green).

    python deadline.py
    python deadline.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv (or NuSMV) and z3.
"""

import os
import sys

from chase_cps import load_spec, refines, repair, viz

HERE = os.path.dirname(os.path.abspath(__file__))


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "deadline.ltl"))
    system = c["Client"].compose(c["Arbiter"]).compose(c["Wait"])
    bound = c["MaxWait"]
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    r = refines(system, bound)
    show(1, "the system refines MaxWait with k = 1", r.status, "invalid")
    if r.guarantees.trace is not None:
        print("   counterexample:")
        print("\n".join("   " + line for line in str(r.guarantees.trace).splitlines()))

    r = repair("refines", system, bound, parameters={"k": (0, 9, "int")})
    show(2, "the least k", r.values, {"k": 2})
    print(f"   optimal {r.optimal}, {r.method} in {r.rounds} rounds, "
          f"checked by {r.check.guarantees.backend}")

    passing = [k for k in range(10)
               if refines(system, bound.instantiate({"k": k})).status == "valid"]
    show(3, "the least k that passes, checking every k", passing[0] if passing else None, 2)
    # the page: before and after the repair
    pairs = []
    for k in (1, 2):
        both = c["Client"].compose(c["Arbiter"]).compose(c["Wait"])
        b = bound.instantiate({"k": k}, name="MaxWait" if k == 1 else "MaxWait_repaired")
        pairs.append((both, b, refines(both, b)))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=pairs, open=[b for _, b, _ in pairs],
                                title="Deadline: before and after the repair"),
                    os.path.join(HERE, "out", "deadline.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
