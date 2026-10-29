"""AHB arbiter: two viewpoints of one component, merged.

The question: two teams wrote two viewpoints of the arbiter of the AMBA AHB
bus, which gives the bus to one of two masters, and lets a master lock it
(requirements.txt, simplified from Bloem et al., COCV 2007). Is there an
arbiter that meets both viewpoints, and what must it assume of the masters?

The viewpoints are written in SystemVerilog Assertions (sva/): Grant (the
bus is given to one master, and no master waits forever) and Lock (a master
that has locked the bus keeps it while it asks for it). This script follows
the design with the CHASE Python package (pip install chase-cps):

  1. Each viewpoint is realizable on its own.
  2. Arbiter = Grant . Lock, the merge, without the assumption LA2 of Lock
     (a master that has locked the bus stops asking for it sooner or later),
     is unrealizable. Its unrealizable core is GR1, GR2, GR3.2, LK1, LK2.1:
     master 1 locks the bus and keeps asking for it, Lock lets it keep the
     bus, and Grant says that master 2 does not wait forever.
  3. With LA2, the merge is realizable. A controller is synthesized, and
     the merge is written as SVA (out/arbiter.sv), for a tool that reads
     SVA.
  4. The controller implements the merge.

The page out/arbiter.html draws the two merges, with their realizability
and the core, and the controller.

    python ahb.py
    python ahb.py --expect     # exit code 1 when a result is not the expected one

The checks need slugs (realizability, synthesis) and nuXmv or NuSMV (the
controller).
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import sys
import time

from chase_cps import (Component, Model, is_implementation, is_realizable, parse_sva, synthesize,
                       to_sva, viz)

HERE = os.path.dirname(os.path.abspath(__file__))


def read(name: str):
    """The contract of sva/<name>.sv, and the label of each of its formulas."""
    with open(os.path.join(HERE, "sva", f"{name}.sv")) as f:
        r = parse_sva(f.read(), name=name.capitalize())
    assert not r.skipped, r.skipped
    return r.contract, {repr(p.formula): p.label.replace("_", ".") for p in r.properties}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
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
        return status

    grant, labels = read("grant")
    lock, more = read("lock")
    labels.update(more)
    found = {}

    def realizable(c):
        found[c.name] = is_realizable(c, timeout=t)
        return found[c.name].status, ""
    step("1. Grant is realizable", "realizable", lambda: realizable(grant))
    step("   Lock is realizable", "realizable", lambda: realizable(lock))

    # Lock without LA2, its only liveness assumption
    lock_without = dataclasses.replace(
        lock, name="Lock_without_LA2",
        assumptions=[a for a in lock.assumptions if labels.get(repr(a)) != "LA2"])

    def without_la2():
        merged = grant.merge(lock_without, name="Arbiter_without_LA2", discharge=True, timeout=t)
        r = is_realizable(merged, core=True, timeout=t)
        found["without"] = merged, r
        text = ""
        if r.core is not None and r.core.core is not None:
            core = sorted(labels.get(repr(g), "?") for g in r.core.core.guarantees)
            text = "   unrealizable core: " + ", ".join(core)
        return r.status, text
    step("2. Grant merged with Lock, without LA2, is realizable", "unrealizable", without_la2)

    arbiter = grant.merge(lock, name="Arbiter", discharge=True, timeout=t)

    def synthesis():
        r = synthesize(arbiter, timeout=t)
        found["controller"] = r
        text = (f"   Arbiter = Grant merged with Lock: {len(arbiter.assumptions)} assumptions, "
                f"{len(arbiter.guarantees)} guarantees")
        if r.controller:
            text += f"\n   controller with {len(r.controller['nodes'])} states"
        return r.status, text
    step("3. Grant merged with Lock is realizable", "realizable", synthesis)

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = os.path.join(HERE, "out", "arbiter.sv")
    with open(out, "w") as f:
        f.write(to_sva(arbiter, clock="clk"))
    print(f"   Arbiter as SVA: {os.path.relpath(out, HERE)}")

    merged, r = found["without"]
    shown = [arbiter, merged]
    if found["controller"].controller is None:
        print("\n4. no controller: skipped")
    else:
        model = Model.from_controller(found["controller"], arbiter)
        controller = Component("Controller", arbiter, model)
        controller.status = step("4. The controller implements Arbiter", "valid",
                                 lambda: (is_implementation(model, arbiter, timeout=t).status, ""))
        shown.append(controller)

    checks = [(grant, found["Grant"]), (lock, found["Lock"]), (arbiter, found["controller"]),
              (merged, r)]
    page = viz.save(viz.diagram(*shown, checks=checks, title="AHB arbiter"),
                    os.path.join(HERE, "out", "arbiter.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
