"""AHB arbiter: two viewpoints of one component, merged or conjoined.

The arbiter of the AMBA AHB bus gives the bus to one of two masters, and a
master can lock the bus (requirements.txt, simplified from Bloem et al.,
COCV 2007). ahb.ltl has two viewpoints of the arbiter: Grant (the bus is
given to one master, and no master waits forever) and Lock (a master that
has locked the bus keeps it while it asks for it, under the assumption that
it stops asking sooner or later). This script follows the design with the
CHASE Python package (pip install chase-cps):

  1. Each viewpoint is realizable.
  2. The merge of the viewpoints, (A1 & A2, (G1 & G2) | !(A1 & A2)), is the
     arbiter: it is equivalent to the contract with the assumptions of Lock
     and the guarantees of both, which is realizable, and a controller is
     synthesized.
  3. The conjunction of the viewpoints, (A1 | A2, G1 & G2), refines the
     merge, and the merge does not refine it: the conjunction asks for each
     viewpoint on its own, so the masters must not wait forever even when a
     master keeps the bus locked.
  4. The controller implements the merge, and not the conjunction. The
     counterexample: master 2 locks the bus and never stops asking, and
     master 1 waits forever. No arbiter can do better: it would have to let
     master 2 keep the bus (Lock) and take it from it (Grant).

    python ahb.py
    python ahb.py --expect     # exit code 1 when a result is not the expected one

The checks need slugs (realizability, synthesis) and nuXmv or NuSMV
(refinement, the controller).
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import Contract, Model, load_spec, implements, is_realizable, refines, synthesize

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "ahb.ltl")
SIGNALS = ("req1", "lock1", "req2", "lock2", "grant1", "grant2", "locked")


def trace(result) -> str:
    """The steps of a counterexample, one line per step."""
    t = result.trace
    lines = []
    for i, state in enumerate(t.prefix + t.loop):
        loop = "  <- loop" if t.loop and i == len(t.prefix) else ""
        lines.append(f"      {i}: " + " ".join(f"{s}={int(bool(state.get(s)))}"
                                              for s in SIGNALS) + loop)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    c = load_spec(SPEC)
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

    grant, lock = c["Grant"], c["Lock"]
    step("1. Grant is realizable", "realizable",
         lambda: (is_realizable(grant, timeout=t).status, ""))
    step("   Lock is realizable", "realizable",
         lambda: (is_realizable(lock, timeout=t).status, ""))

    merged = grant.merge(lock, name="Merged")
    conjoined = grant.conjoin(lock, name="Conjoined")
    # the merge, with the assumptions of Lock and the guarantees of both
    arbiter = Contract("Arbiter", dict(merged.inputs), dict(merged.outputs),
                       list(lock.assumptions), list(grant.guarantees) + list(lock.guarantees))

    def same():
        both = (refines(arbiter, merged, timeout=t).status == "valid"
                == refines(merged, arbiter, timeout=t).status)
        return ("equivalent" if both else "different"), ""
    step("2. The merge of Grant and Lock is equivalent to Arbiter", "equivalent", same)

    found = {}

    def synthesis():
        r = synthesize(arbiter, timeout=t)
        found["controller"] = r
        text = f"   controller with {len(r.controller['nodes'])} states" if r.controller else ""
        return r.status, text
    step("   Arbiter is realizable", "realizable", synthesis)

    step("3. The conjunction refines Arbiter", "valid",
         lambda: (refines(conjoined, arbiter, timeout=t).status, ""))
    step("   Arbiter refines the conjunction", "invalid",
         lambda: (refines(arbiter, conjoined, timeout=t).status, ""))

    if found["controller"].controller is None:
        print("\n4. no controller: skipped")
    else:
        model = Model.from_controller(found["controller"], arbiter)
        step("4. The controller implements Arbiter", "valid",
             lambda: (implements(model, arbiter, timeout=t).status, ""))

        def conjunction():
            r = implements(model, conjoined, timeout=t)
            text = "   a counterexample:\n" + trace(r) if r.trace is not None else ""
            return r.status, text
        step("   The controller implements the conjunction", "invalid", conjunction)

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
