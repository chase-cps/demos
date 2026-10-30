"""A small factory: requirements from patterns.

The factory of the FDL 2024 paper is written in the domain-specific language
of CHASE (dsl_factory_realizable.txt): a warehouse, conveyors, machines that
turn iron into coins, pipes, output bays, and the gates between them. CHASE
turns the patterns of requirements into one GR(1) contract for the
controller of the gates. This script checks it with the CHASE Python package
(pip install chase-cps):

  1. The requirements are realizable: the controller can open and close the
     gates so that the output bays keep their supply when main conveyors
     fail.

    python factory.py
    python factory.py --expect     # exit code 1 when a result is not the expected one

The check needs slugs.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import is_realizable, load_dsl, viz

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="time limit of the check, in seconds")
    args = parser.parse_args()

    factory = load_dsl(os.path.join(HERE, "dsl_factory_realizable.txt"), name="Factory")
    print(f"The factory: {len(factory.inputs)} inputs, {len(factory.outputs)} outputs, "
          f"{len(factory.assumptions)} assumptions, {len(factory.guarantees)} guarantees")

    start = time.time()
    r = is_realizable(factory, timeout=args.timeout)
    wrong = r.status != "realizable"
    print(f"\n1. The requirements are realizable: {r.status} [{time.time() - start:.1f} s]"
          + ("   (expected realizable)" if wrong else ""))

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(factory, checks=[(factory, r)], open=[factory],
                                title="A small factory: requirements from patterns"),
                    os.path.join(HERE, "out", "factory.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
