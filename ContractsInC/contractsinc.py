"""ContractsInC: contracts written in the C file, next to the code.

tank.c has the clauses of ESBMC (__ESBMC_requires, __ESBMC_ensures),
ring.c those of CBMC (__CPROVER_requires, __CPROVER_ensures). load_c reads
each function of a file as a contract (the requires clauses are its
assumptions, the ensures clauses its guarantees) and the function as its
implementation; ESBMC (or CBMC) checks the function against it. A function
with no clause is checked alone: no overflow, division by zero, access out
of bounds, or failed assert.

  1. pump (tank.c) meets its contract: full speed from a level of 80, off
     below 20.
  2. flow has no clause; the code alone fails: liters / seconds overflows
     for liters = INT_MIN and seconds = -1 (and seconds = 0 divides by
     zero).
  3. advance (ring.c), the next slot of a ring buffer of 8 slots, meets its
     contract: the slot stays in the buffer, and is the next one but at the
     end.
  4. advance_fast, without the wrap at the end, does not: i = 7 gives
     ni = 8.
  5. limit (climb.c, in ACSL, the language of Frama-C), the climb rate of
     the drone of DroneAltitude, meets its contract: at most 3 up or down.
  6. limit_loose, with the test of the top written v > 4, does not: v = 4
     gives 4.

The pages out/tank.html, out/ring.html, and out/climb.html draw each file: each
function is a component with its code (chase-cps view FILE.c --check).

    python contractsinc.py
    python contractsinc.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys

from chase_cps import is_implementation, load_c, viz

HERE = os.path.dirname(os.path.abspath(__file__))
WANT = {"pump": "valid", "flow": "invalid", "advance": "valid", "advance_fast": "invalid",
        "limit": "valid", "limit_loose": "invalid"}


def main(expect: bool) -> int:
    ok = []
    for step, file in ((1, "tank.c"), (3, "ring.c"), (5, "climb.c")):
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
