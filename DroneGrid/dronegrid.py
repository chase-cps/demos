"""DroneGrid: the C code of two drones, checked part by part through contracts.

One step of two drones of the fire-suppression federation of ContrACT
(MDFS): each drone asks for a move toward its target (plan.c), the
coordinator grants the moves (coordinator.c), and each drone moves as
granted (move.c). dronegrid.ltl has a contract for each function, and the
requirement Fleet: two drones in different cells are still in different
cells after the step, and do not cross each other. This script follows the
design with the CHASE Python package (pip install chase-cps[z3], and ESBMC
or CBMC for the C code):

  1. The contracts of the parts, composed, do not refine Fleet (z3): when
     the two drones would swap cells, the coordinator stops drone 1, and
     drone 0 moves into the cell where drone 1 stays.
  2. The same with drone 1 at its target: it stays, and drone 0 moves into
     its cell; the coordinator checks only drones that both move.
  3. CoordinatorSafe grants a move only into a cell that is free after the
     step: the composition refines Fleet. No value can fix Coordinator (the
     check reads no constant): its rule must change. The quotient of Fleet
     by the other parts is the weakest contract of the coordinator:
     Coordinator does not refine it, CoordinatorSafe does.
  4. Each C function implements its contract (ESBMC): plan0, plan1, move0,
     move1, and grant, the reaction as written. grant does not implement
     CoordinatorSafe; grant_safe does. With grant_safe, each function
     implements its contract and the contracts refine Fleet: the step of
     the C code keeps the drones apart, shown one function at a time.

The page out/dronegrid.html draws the step before and after the fix: each
function is a component with its C code inside Fleet.

    python dronegrid.py
    python dronegrid.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys

from chase_cps import CFunction, Component, System, is_implementation, load_spec, refines, viz

HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = ("x0", "y0", "tx0", "ty0", "r0", "g0", "nx0", "ny0", "x1", "y1", "tx1", "ty1", "r1", "g1", "nx1", "ny1")


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "dronegrid.ltl"))
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    def step(coordinator):
        return (c["Plan0"].compose(c["Plan1"]).compose(c[coordinator])
                .compose(c["Move0"]).compose(c["Move1"]))

    def trace(r):
        t = r.guarantees.trace
        s = (t.prefix + t.loop)[0]
        print("   " + ", ".join(f"{k}={s[k]}" for k in SHOW if k in s))

    r = refines(step("Coordinator"), c["Fleet"])
    show(1, "the parts with Coordinator refine Fleet", r.status, "invalid")
    trace(r)
    r = refines(step("Coordinator"), c["Fleet"], context=["x1 = tx1 & y1 = ty1"])
    show(2, "the same, drone 1 at its target", r.status, "invalid")
    trace(r)
    r = refines(step("CoordinatorSafe"), c["Fleet"])
    show(3, "the parts with CoordinatorSafe refine Fleet", r.status, "valid")
    # what the coordinator must do: the quotient of Fleet by the other parts
    others = c["Plan0"].compose(c["Plan1"]).compose(c["Move0"]).compose(c["Move1"])
    needs = c["Fleet"].divide(others, name="CoordinatorNeeds")
    show(3, "Coordinator refines the quotient Fleet / (the other parts)",
         refines(c["Coordinator"], needs).status, "invalid")
    show(3, "CoordinatorSafe refines it", refines(c["CoordinatorSafe"], needs).status, "valid")

    def code(file, function):
        return CFunction(os.path.join(HERE, file), function)
    functions = [("plan.c", "plan0", "Plan0"), ("plan.c", "plan1", "Plan1"),
                 ("coordinator.c", "grant", "Coordinator"),
                 ("move.c", "move0", "Move0"), ("move.c", "move1", "Move1")]
    status = {}
    for file, function, contract in functions + [("coordinator.c", "grant", "CoordinatorSafe"),
                                                 ("coordinator.c", "grant_safe", "CoordinatorSafe")]:
        r = is_implementation(code(file, function), c[contract])
        status[(function, contract)] = r          # the result: the page shows its counterexample
        want = "invalid" if (function, contract) == ("grant", "CoordinatorSafe") else "valid"
        show(4, f"{function} in {file} implements {contract}", r.status, want)

    # the page: the step before and after the fix, each function with its code
    pairs = []
    for coordinator, grant, name in (("Coordinator", "grant", "Fleet"), ("CoordinatorSafe", "grant_safe", "Fleet_safe")):
        parts = []
        for file, function, contract in functions:
            if contract == "Coordinator":
                contract, function = coordinator, grant
            parts.append(Component(contract, c[contract], code(file, function),
                                   status=status[(function, contract)]))
        fleet = c["Fleet"].instantiate({}, name=name)
        pairs.append((System("Step", parts), fleet, refines(step(coordinator), fleet)))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=pairs, title="DroneGrid: the step of two drones, before and after the fix"),
                    os.path.join(HERE, "out", "dronegrid.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
