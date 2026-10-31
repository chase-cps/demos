"""ContractsInC: contracts written in the C file, next to the code.

thermostat.c has the clauses of ESBMC (__ESBMC_requires, __ESBMC_ensures),
move.c those of CBMC (__CPROVER_requires, __CPROVER_ensures). load_c reads
each function of a file as a contract (the requires clauses are its
assumptions, the ensures clauses its guarantees) and the function as its
implementation; ESBMC (or CBMC) checks the function against it. A function
with no clause is checked alone: no overflow, division by zero, access out
of bounds, or failed assert.

  1. thermostat (thermostat.c) meets its contract: it heats while T < 74.
  2. heat_per_area has no clause; the code alone fails: power / area
     overflows for power = INT_MIN and area = -1 (and area = 0 divides by
     zero).
  3. move (move.c), the move of a drone of DroneGrid, meets its contract:
     the drone stays on the grid, and moves right when asked and not at
     the edge.
  4. move_fast, without the test at the edge, does not: x = 9, g = 1 gives
     nx = 10.
  5. limit (climb.c, in ACSL, the language of Frama-C), the climb rate of
     the drone of DroneAltitude, meets its contract: at most 3 up or down.
  6. limit_loose, with the test of the top written v > 4, does not: v = 4
     gives 4.

The pages out/thermostat.html, out/move.html, and out/climb.html draw each file: each
function is a component with its code (chase-cps view FILE.c --check).

    python contractsinc.py
    python contractsinc.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys

from chase_cps import is_implementation, load_c, viz

HERE = os.path.dirname(os.path.abspath(__file__))
WANT = {"thermostat": "valid", "heat_per_area": "invalid", "move": "valid", "move_fast": "invalid",
        "limit": "valid", "limit_loose": "invalid"}


def main(expect: bool) -> int:
    ok = []
    for step, file in ((1, "thermostat.c"), (3, "move.c"), (5, "climb.c")):
        functions = load_c(os.path.join(HERE, file))
        for k, (name, (contract, function)) in enumerate(functions.items()):
            r = is_implementation(function, contract)
            ok.append(r.status == WANT[name])
            alone = not contract.assumptions and not contract.guarantees
            print(f"step {step + k}: {name} in {file}", "is safe code" if alone else "meets its contract",
                  "->", r.status, "" if r.status == WANT[name] else f"   (expected {WANT[name]})")
            if r.status == "invalid" and getattr(r, "trace", None):
                call = (r.trace.prefix + r.trace.loop)[0]
                print("    a call:", ", ".join(f"{v} = {x}" for v, x in call.items()))
            if getattr(r, "reason", None):
                print("    " + r.reason)
        # the page: each function a component with its code, checked (as chase-cps view FILE.c --check)
        out = os.path.join(HERE, "out", file.replace(".c", ".html"))
        with open(out, "w") as f:
            f.write(viz.html(viz.from_spec(os.path.join(HERE, file), check=True)))
    print("all as expected" if all(ok) else "some results are not the expected ones")
    return 0 if all(ok) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
