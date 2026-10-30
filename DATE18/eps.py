"""Power systems: requirements from patterns.

The requirements of the electrical power system of an aircraft are written
in the domain-specific language of CHASE: the components, how they are
connected, and patterns of requirements (template_0_unrealizable.txt). CHASE
turns them into one GR(1) contract for the controller of the contactors.
This script follows the DATE 2018 paper with the CHASE Python package (pip
install chase-cps):

  1. The requirements as written are unrealizable. The unrealizable core is
     the pattern that never connects two generators in parallel, and the one
     that never leaves the left DC bus unpowered for more than 15 ms.
  2. With 30 ms without power for a DC bus and 20 ms to disconnect a failed
     generator (template_0_realizable.txt), the requirements are realizable.
  3. The same language describes a small factory (FDL 2024,
     ../FDL2024/dsl_factory_realizable.txt); its requirements are realizable.

    python eps.py
    python eps.py --expect     # exit code 1 when a result is not the expected one

The checks need slugs.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import is_realizable, load_dsl, ltl, viz

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    wrong = []

    def step(title, expected, contract, core=False):
        start = time.time()
        r = is_realizable(contract, core=core, timeout=args.timeout)
        mark = "" if r.status == expected else f"   (expected {expected})"
        print(f"\n{title}: {r.status} [{time.time() - start:.1f} s]{mark}")
        if r.status != expected:
            wrong.append(title)
        return r

    eps15 = load_dsl(os.path.join(HERE, "template_0_unrealizable.txt"), name="EPS_15ms")
    eps30 = load_dsl(os.path.join(HERE, "template_0_realizable.txt"), name="EPS_30ms")
    factory = load_dsl(os.path.join(HERE, "..", "FDL2024", "dsl_factory_realizable.txt"),
                       name="Factory")
    print(f"The power system: {len(eps15.inputs)} inputs, {len(eps15.outputs)} outputs, "
          f"{len(eps15.assumptions)} assumptions, {len(eps15.guarantees)} guarantees")

    first = step("1. The requirements as written are realizable", "unrealizable", eps15, core=True)
    if first.core is not None:
        kept = first.core.core.guarantees
        print(f"   the unrealizable core: {len(kept)} of {len(eps15.guarantees)} guarantees")
        for g in kept:
            text = ltl.to_str(g)
            print("      " + (text if len(text) <= 100 else text[:97] + "..."))
    second = step("2. With 30 ms for a DC bus, realizable", "realizable", eps30)
    third = step("3. The factory, realizable", "realizable", factory)

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(eps15, eps30, factory,
                                checks=[(eps15, first), (eps30, second), (factory, third)],
                                open=[eps15], title="Power systems: requirements from patterns"),
                    os.path.join(HERE, "out", "eps.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
